from django.db import models
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.primitives import padding
from django.contrib.auth.models import User
import hashlib
import bleach
from bs4 import BeautifulSoup

class Note(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='notes', null=True, blank=True, default=None)
    title = models.CharField(max_length=200, blank=False, null=False)
    content = models.TextField()
    public = models.BooleanField(default=False, blank=True)
    encrypted = models.BooleanField(default=False, blank=True)
    password = models.TextField(blank=True, default="")

    def __str__(self):
        return self.title
    
    def pre_cleaning(self, content):
        soup = BeautifulSoup(content, 'html.parser')
        
        for img_tag in soup.find_all('img'):
            src = img_tag['src']
            if (not (str(src).startswith('http') or str(src).startswith('https'))) or "javascript:" in str(src):
                img_tag['src'] = ''
                
        for img_tag in soup.find_all('a'):
            src = img_tag['href']
            if (not (str(src).startswith('http') or str(src).startswith('https'))) or "javascript:" in str(src):
                img_tag['href'] = ''
        return str(soup)
    
    def save(self, *args, **kwargs):
        if self.public:
            self.encrypted = False
        
        allowed_tags = ['h1', 'h2', 'h3', 'h4', 'h5', 'b', 'a', 'b', 'i', 'img']
        allowed_attributes = {'img': ['src'], 'a': ['href']}
        
        almost_cleaned_content = self.pre_cleaning(self.content)
        cleaned_content = bleach.clean(almost_cleaned_content, tags=allowed_tags, attributes=allowed_attributes)
        self.content = cleaned_content
        
        if self.encrypted:
            text = self.content
            password = self.password
            
            salt_length = len(str(self.title)) % 5
            salt = f"g7{str(self.title).ljust(salt_length)}pj"
            salted_password = salt + password
            hasher = hashlib.sha256()
            password_bytes = salted_password.encode('utf-8')
            hasher.update(password_bytes)
            hashed_password = hasher.hexdigest()
            
            key = hashed_password.ljust(32)[:32].encode()
            cipher = Cipher(algorithms.AES(key), modes.ECB(), backend=default_backend())
            encryptor = cipher.encryptor()
            padder = padding.PKCS7(128).padder()
            padded_data = padder.update(text.encode('utf-8')) + padder.finalize()
            encrypted_data = encryptor.update(padded_data) + encryptor.finalize()
            encrypted_text = encrypted_data.decode('latin-1')
            
            self.password = hashed_password
            self.content = encrypted_text
        
        super().save(*args, **kwargs)

    def get_decrypted_text(self, password):
        if not self.encrypted:
            return self.content
        
        salt_length = len(str(self.title)) % 5
        salt = f"g7{str(self.title).ljust(salt_length)}pj"
        salted_password = salt + password
        hasher = hashlib.sha256()
        password_bytes = salted_password.encode('utf-8')
        hasher.update(password_bytes)
        hashed_password = hasher.hexdigest()
        
        if hashed_password != self.password:
            raise Exception('Wrong password')
        
        key = hashed_password.ljust(32)[:32].encode()
        cipher = Cipher(algorithms.AES(key), modes.ECB(), backend=default_backend())
        decryptor = cipher.decryptor()
        encrypted_data = self.content.encode('latin-1')
        decrypted_data = decryptor.update(encrypted_data) + decryptor.finalize()
        unpadder = padding.PKCS7(128).unpadder()
        upadded_data = unpadder.update(decrypted_data) + unpadder.finalize()
        
        decrypted_text = upadded_data.decode('utf-8')
        
        return decrypted_text
    
    def get_encrypted_text(self):
        return self.content