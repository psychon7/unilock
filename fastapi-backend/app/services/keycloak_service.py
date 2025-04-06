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

    async def list_clients(self, realm: str):
        """List all clients (applications) in the specified realm"""
        try:
            self.admin.realm_name = realm
            clients = self.admin.get_clients()
            logger.info(f"Retrieved {len(clients)} clients for realm {realm}")
            # Optionally filter or map fields if needed before returning
            return clients
        except Exception as e:
            logger.error(f"Failed to list clients for realm {realm}: {e}")
            raise HTTPException(
                status_code=400,
                detail=f"Keycloak error while listing clients: {str(e)}"
            )

    async def list_identity_providers(self, realm: str):
        """List all identity providers in the specified realm"""
        try:
            self.admin.realm_name = realm
            idps = self.admin.get_idps()
            logger.info(f"Retrieved {len(idps)} identity providers for realm {realm}")
            return idps
        except Exception as e:
            logger.error(f"Failed to list identity providers for realm {realm}: {e}")
            raise HTTPException(
                status_code=400,
                detail=f"Keycloak error while listing identity providers: {str(e)}"
            )

    async def get_identity_provider(self, realm: str, alias: str):
        """Get details of a specific identity provider"""
        try:
            self.admin.realm_name = realm
            idp = self.admin.get_idp(alias)
            logger.info(f"Retrieved identity provider {alias} for realm {realm}")
            return idp
        except Exception as e:
            logger.error(f"Failed to get identity provider {alias} for realm {realm}: {e}")
            raise HTTPException(
                status_code=404,
                detail=f"Identity provider not found or inaccessible: {alias}"
            )

    async def update_identity_provider_state(self, realm: str, alias: str, enabled: bool):
        """Enable or disable an identity provider"""
        try:
            self.admin.realm_name = realm
            idp = self.admin.get_idp(alias)
            idp['enabled'] = enabled
            self.admin.update_idp(alias, idp)
            logger.info(f"Updated identity provider {alias} state to enabled={enabled} in realm {realm}")
            return {"status": "success", "enabled": enabled}
        except Exception as e:
            logger.error(f"Failed to update identity provider {alias} state in realm {realm}: {e}")
            raise HTTPException(
                status_code=400,
                detail=f"Failed to update identity provider state: {str(e)}"
            )

    async def get_theme(self, realm: str) -> dict:
        """Get theme configuration for a realm"""
        try:
            self.admin.realm_name = realm
            realm_data = self.admin.get_realm()
            
            # Extract theme-related settings from realm data
            theme_config = {
                "primaryColor": realm_data.get("attributes", {}).get("primaryColor", "#3b82f6"),
                "secondaryColor": realm_data.get("attributes", {}).get("secondaryColor", "#6b7280"),
                "logoUrl": realm_data.get("attributes", {}).get("logoUrl"),
                "loginTheme": realm_data.get("loginTheme")
            }
            
            logger.info(f"Retrieved theme config for realm {realm}")
            return theme_config
        except Exception as e:
            logger.error(f"Failed to get theme config for realm {realm}: {e}")
            raise HTTPException(
                status_code=404,
                detail=f"Failed to get theme configuration: {str(e)}"
            )

    async def update_theme(self, realm: str, theme_config: dict) -> dict:
        """Update theme configuration for a realm"""
        try:
            self.admin.realm_name = realm
            realm_data = self.admin.get_realm()
            
            # Update realm attributes with theme config
            attributes = realm_data.get("attributes", {})
            attributes.update({
                "primaryColor": theme_config["primaryColor"],
                "secondaryColor": theme_config["secondaryColor"],
            })
            if theme_config.get("logoUrl"):
                attributes["logoUrl"] = theme_config["logoUrl"]
            
            # Update realm data
            update_data = {
                "attributes": attributes,
                "loginTheme": theme_config.get("loginTheme", realm_data.get("loginTheme"))
            }
            
            self.admin.update_realm(realm, update_data)
            logger.info(f"Updated theme config for realm {realm}")
            
            return await self.get_theme(realm)
        except Exception as e:
            logger.error(f"Failed to update theme config for realm {realm}: {e}")
            raise HTTPException(
                status_code=400,
                detail=f"Failed to update theme configuration: {str(e)}"
            )

    async def upload_logo(self, realm: str, logo_file: bytes, filename: str) -> str:
        """Upload a logo for a realm and return its URL"""
        try:
            # TODO: Implement actual file storage (e.g., S3, local filesystem)
            # For now, we'll assume a local storage path
            import os
            from pathlib import Path
            
            # Create logos directory if it doesn't exist
            logos_dir = Path("static/logos")
            logos_dir.mkdir(parents=True, exist_ok=True)
            
            # Generate unique filename
            file_ext = os.path.splitext(filename)[1]
            unique_filename = f"{realm}_logo{file_ext}"
            file_path = logos_dir / unique_filename
            
            # Save the file
            with open(file_path, "wb") as f:
                f.write(logo_file)
            
            # Generate URL (in production, this would be a CDN or proper static file URL)
            logo_url = f"/static/logos/{unique_filename}"
            
            # Update realm with logo URL
            await self.update_theme(realm, {"logoUrl": logo_url})
            
            logger.info(f"Uploaded logo for realm {realm}")
            return logo_url
        except Exception as e:
            logger.error(f"Failed to upload logo for realm {realm}: {e}")
            raise HTTPException(
                status_code=400,
                detail=f"Failed to upload logo: {str(e)}"
            )
