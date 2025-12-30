"""
Servicio para generar códigos QR y subirlos a Google Drive
"""
import os
import io
import qrcode
from PIL import Image
from googleapiclient.http import MediaIoBaseUpload
from app.services.sheets_writer import get_credentials
from googleapiclient.discovery import build
from config import Config


# ID de la carpeta de Google Drive donde se guardarán los QR
QR_FOLDER_ID = '1kT3055GjSqb0IWH1Dg7gZGPipcR55D-r'
QR_FOLDER_NAME = 'QR'


class QRService:
    """
    Servicio para generar y gestionar códigos QR
    """
    
    @staticmethod
    def generate_qr_code(url: str, filename: str = None) -> io.BytesIO:
        """
        Generar código QR como imagen en memoria
        
        Args:
            url: URL a codificar en el QR
            filename: Nombre del archivo (opcional, solo para logging)
        
        Returns:
            BytesIO con la imagen del QR
        """
        try:
            # Crear instancia de QRCode
            qr = qrcode.QRCode(
                version=1,
                error_correction=qrcode.constants.ERROR_CORRECT_L,
                box_size=10,
                border=4,
            )
            qr.add_data(url)
            qr.make(fit=True)
            
            # Crear imagen
            img = qr.make_image(fill_color="black", back_color="white")
            
            # Convertir a BytesIO
            img_bytes = io.BytesIO()
            img.save(img_bytes, format='PNG')
            img_bytes.seek(0)
            return img_bytes
            
        except Exception as e:
            print(f"Error al generar QR: {e}")
            import traceback
            traceback.print_exc()
            return None
    
    @staticmethod
    def get_or_create_qr_folder(service) -> str:
        """
        Obtener o crear la carpeta QR en Google Drive
        
        Args:
            service: Servicio de Google Drive API
        
        Returns:
            ID de la carpeta QR
        """
        try:
            # Buscar carpeta QR en la carpeta padre
            query = f"name='{QR_FOLDER_NAME}' and '{QR_FOLDER_ID}' in parents and mimeType='application/vnd.google-apps.folder' and trashed=false"
            
            results = service.files().list(
                q=query,
                spaces='drive',
                fields='files(id, name)'
            ).execute()
            
            folders = results.get('files', [])
            
            if folders:
                return folders[0]['id']
            else:
                file_metadata = {
                    'name': QR_FOLDER_NAME,
                    'mimeType': 'application/vnd.google-apps.folder',
                    'parents': [QR_FOLDER_ID]
                }
                
                folder = service.files().create(
                    body=file_metadata,
                    fields='id'
                ).execute()
                
                return folder.get('id')
                
        except Exception as e:
            print(f"Error al obtener/crear carpeta QR: {e}")
            return None
    
    @staticmethod
    def upload_qr_to_drive(qr_image: io.BytesIO, filename: str, product_code: str) -> bool:
        """
        Subir código QR a Google Drive
        
        Args:
            qr_image: BytesIO con la imagen del QR
            filename: Nombre del archivo (con extensión .png)
            product_code: Código del producto (para logging)
        
        Returns:
            True si se subió correctamente, False en caso contrario
        """
        try:
            creds = get_credentials()
            service = build('drive', 'v3', credentials=creds)
            
            # Obtener o crear carpeta QR
            folder_id = QRService.get_or_create_qr_folder(service)
            if not folder_id:
                return False
            
            # Verificar si el archivo ya existe
            query = f"name='{filename}' and '{folder_id}' in parents and trashed=false"
            results = service.files().list(
                q=query,
                spaces='drive',
                fields='files(id, name)'
            ).execute()
            
            existing_files = results.get('files', [])
            
            if existing_files:
                # Actualizar archivo existente
                file_id = existing_files[0]['id']
                media = MediaIoBaseUpload(qr_image, mimetype='image/png', resumable=True)
                
                service.files().update(
                    fileId=file_id,
                    media_body=media
                ).execute()
            else:
                file_metadata = {
                    'name': filename,
                    'parents': [folder_id]
                }
                
                media = MediaIoBaseUpload(qr_image, mimetype='image/png', resumable=True)
                
                service.files().create(
                    body=file_metadata,
                    media_body=media,
                    fields='id'
                ).execute()
            
            return True
            
        except Exception as e:
            print(f"Error al subir QR a Drive: {e}")
            import traceback
            traceback.print_exc()
            return False
    
    @staticmethod
    def generate_and_upload_qr(product_id: str, product_code: str, base_url: str = None) -> bool:
        """
        Generar y subir código QR para un producto
        
        Args:
            product_id: ID del producto
            product_code: Código del producto (segunda columna, para el nombre del archivo)
            base_url: URL base de la aplicación (opcional, se detecta automáticamente)
        
        Returns:
            True si se generó y subió correctamente, False en caso contrario
        """
        try:
            # Construir URL de edición del producto
            if base_url is None:
                # Intentar detectar desde la configuración o usar localhost por defecto
                base_url = os.environ.get('BASE_URL', 'http://localhost:5000')
            
            # Asegurar que base_url no termine con /
            base_url = base_url.rstrip('/')
            
            product_url = f"{base_url}/product/detail/{product_id}"
            
            # Generar QR
            qr_image = QRService.generate_qr_code(product_url, product_code)
            if not qr_image:
                return False
            
            # Nombre del archivo: código del producto + .png
            filename = f"{product_code}.png"
            
            # Subir a Drive
            success = QRService.upload_qr_to_drive(qr_image, filename, product_code)
            
            return success
            
        except Exception as e:
            print(f"Error al generar y subir QR: {e}")
            import traceback
            traceback.print_exc()
            return False

