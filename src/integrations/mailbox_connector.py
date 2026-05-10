import os
from typing import List, Optional, Dict
from datetime import datetime
from azure.identity import ClientSecretCredential
from msgraph import GraphServiceClient
from msgraph.generated.users.item.messages.messages_request_builder import MessagesRequestBuilder
from kiota_abstractions.base_request_configuration import RequestConfiguration

class MailboxConnector:
    """
    A production-ready connector for Microsoft Graph API to manage email retrieval.
    Uses msgraph-sdk and azure-identity for secure authentication.
    """
    def __init__(self, secrets_provider):
        self.secrets = secrets_provider
        self._client: Optional[GraphServiceClient] = None
        self._mailbox_user_id = os.getenv("GRAPH_MAILBOX_ID")

    def connect(self) -> bool:
        """
        Initializes the GraphServiceClient using credentials from the secrets provider.
        """
        try:
            creds = self.secrets.get_mailbox_credentials()
            client_id = creds.get("client_id")
            client_secret = creds.get("client_secret")
            tenant_id = creds.get("tenant_id")

            if not all([client_id, client_secret, tenant_id]):
                return False

            credential = ClientSecretCredential(
                tenant_id=tenant_id,
                client_id=client_id,
                client_secret=client_secret
            )
            
            self._client = GraphServiceClient(credential)
            return True
        except Exception:
            return False

    def disconnect(self) -> None:
        """
        Clears the client connection.
        """
        self._client = None

    def is_connected(self) -> bool:
        """
        Checks if the client is initialized.
        """
        return self._client is not None

    async def retrieve_emails(self, start_date: datetime, end_date: datetime) -> List[Dict]:
        """
        Filters emails in the shared mailbox by received date range.
        Returns a list of dicts with email metadata and PDF attachments.
        """
        if not self.is_connected():
            if not self.connect():
                return []

        # Filter: receivedDateTime ge start_date and receivedDateTime le end_date
        # Date format: YYYY-MM-DDTHH:MM:SSZ
        start_str = start_date.strftime("%Y-%m-%dT%H:%M:%SZ")
        end_str = end_date.strftime("%Y-%m-%dT%H:%M:%SZ")
        filter_query = f"receivedDateTime ge {start_str} and receivedDateTime le {end_str}"

        query_params = MessagesRequestBuilder.MessagesRequestBuilderGetQueryParameters(
            filter=filter_query,
            expand=["attachments"],
            select=["id", "subject", "receivedDateTime", "hasAttachments"]
        )
        
        request_config = RequestConfiguration(query_parameters=query_params)
        
        try:
            messages_response = await self._client.users.by_user_id(self._mailbox_user_id).messages.get(request_configuration=request_config)
            
            results = []
            if messages_response and messages_response.value:
                for message in messages_response.value:
                    email_data = {
                        "id": message.id,
                        "subject": message.subject,
                        "received_date": message.received_date_time,
                        "attachments": []
                    }
                    
                    if message.has_attachments:
                        attachments_response = await self._client.users.by_user_id(self._mailbox_user_id).messages.by_message_id(message.id).attachments.get()
                        if attachments_response and attachments_response.value:
                            for attachment in attachments_response.value:
                                # Check if it's a file attachment and a PDF
                                if hasattr(attachment, "content_bytes") and attachment.name.lower().endswith(".pdf"):
                                    email_data["attachments"].append({
                                        "filename": attachment.name,
                                        "content": attachment.content_bytes
                                    })
                    results.append(email_data)
            return results
        except Exception:
            return []

    async def get_unread_emails_with_attachments(self) -> List[Dict]:
        """
        Finds unread messages with attachments, specifically filtering for .pdf files.
        Returns bytes for the PDF content within the email dict.
        """
        if not self.is_connected():
            if not self.connect():
                return []

        # Filter: isRead eq false and hasAttachments eq true
        filter_query = "isRead eq false and hasAttachments eq true"

        query_params = MessagesRequestBuilder.MessagesRequestBuilderGetQueryParameters(
            filter=filter_query,
            expand=["attachments"],
            select=["id", "subject", "receivedDateTime"]
        )
        
        request_config = RequestConfiguration(query_parameters=query_params)

        try:
            messages_response = await self._client.users.by_user_id(self._mailbox_user_id).messages.get(request_configuration=request_config)
            
            results = []
            if messages_response and messages_response.value:
                for message in messages_response.value:
                    email_data = {
                        "id": message.id,
                        "subject": message.subject,
                        "received_date": message.received_date_time,
                        "attachments": []
                    }
                    
                    # Fetch detailed attachments
                    attachments_response = await self._client.users.by_user_id(self._mailbox_user_id).messages.by_message_id(message.id).attachments.get()
                    if attachments_response and attachments_response.value:
                        for attachment in attachments_response.value:
                            # We only care about file attachments that are PDFs
                            from msgraph.generated.models.file_attachment import FileAttachment
                            if isinstance(attachment, FileAttachment) and attachment.name.lower().endswith(".pdf"):
                                email_data["attachments"].append({
                                    "filename": attachment.name,
                                    "content": attachment.content_bytes
                                })
                    
                    if email_data["attachments"]:
                        results.append(email_data)
                        
            return results
        except Exception:
            return []
