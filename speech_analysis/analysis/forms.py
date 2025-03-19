from django import forms

class AudioFileForm(forms.Form):
    audio_file = forms.FileField()

from django.core.validators import FileExtensionValidator

class AudioFileForm(forms.Form):
    audio_file = forms.FileField (
        validators=[FileExtensionValidator(allowed_extensions=['wav', 'mp3'])]
    )