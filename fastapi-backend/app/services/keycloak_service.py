from python_keycloak import KeycloakAdmin
from loguru import logger
from fastapi import HTTPException
from app.core.settings import settings

class KeycloakService:
    def __init__(self):
        """Initialize Keycloak admin client with settings"""
        try:
            self.admin = KeycloakAdmin(
                server_url=str(settings.KEYCLOAK_URL),
                username=settings.KEYCLOAK_ADMIN_USERNAME,
                password=settings.KEYCLOAK_ADMIN_PASSWORD,
                realm_name=settings.KEYCLOAK_REALM,
                verify=True
            )
            logger.info("Successfully connected to Keycloak Admin API")
        except Exception as e:
            logger.error(f"Failed to initialize Keycloak admin client: {e}")
            raise HTTPException(
                status_code=500,
                detail="Failed to connect to Keycloak admin interface"
            )

    async def create_realm(self, realm_name: str, display_name: str):
        """Create a new realm with basic configuration"""
        try:
            self.admin.create_realm({
                "realm": realm_name,
                "displayName": display_name,
                "enabled": True,
                "registrationAllowed": False,
                "loginWithEmailAllowed": True
            })
            logger.info(f"Created new realm: {realm_name}")
            return {"status": "success", "realm": realm_name}
        except Exception as e:
            logger.error(f"Failed to create realm {realm_name}: {e}")
            raise HTTPException(
                status_code=400,
                detail=f"Keycloak error: {str(e)}"
            )

    async def create_client(self, realm: str, client_id: str, redirect_uris: list[str]):
        """Create a new client in the specified realm"""
        try:
            self.admin.realm_name = realm  # Switch to target realm
            client = self.admin.create_client({
                "clientId": client_id,
                "redirectUris": redirect_uris,
                "publicClient": True,
                "enabled": True,
                "standardFlowEnabled": True,
                "implicitFlowEnabled": False,
                "directAccessGrantsEnabled": True
            })
            logger.info(f"Created client {client_id} in realm {realm}")
            return client
        except Exception as e:
            logger.error(f"Failed to create client {client_id}: {e}")
            raise HTTPException(
                status_code=400,
                detail=f"Keycloak error: {str(e)}"
            )

    async def get_realm_info(self, realm: str):
        """Get information about a specific realm"""
        try:
            self.admin.realm_name = realm
            return self.admin.get_realm()
        except Exception as e:
            logger.error(f"Failed to get realm info for {realm}: {e}")
            raise HTTPException(
                status_code=404,
                detail=f"Realm not found or inaccessible: {realm}"
            )
