from django import forms
from django.core.validators import RegexValidator
from .models import ForestDivision, ForestStation, Animal, PreservedAnimal
import re


class ForestDivisionForm(forms.ModelForm):
    """
    Form for adding/editing Forest Divisions with validation.
    Ensures Division Name and Location contain only alphabets and spaces.
    """
    
    class Meta:
        model = ForestDivision
        fields = ['name', 'location', 'description']
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'e.g., Wayanad North',
                'required': True,
                'pattern': '[A-Za-z\\s]+',
                'title': 'Only alphabets and spaces are allowed'
            }),
            'location': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'e.g., Palakkad',
                'pattern': '[A-Za-z\\s]+',
                'title': 'Only alphabets and spaces are allowed'
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 4,
                'placeholder': 'Enter description (optional)'
            }),
        }
        labels = {
            'name': 'Division Name *',
            'location': 'Location',
            'description': 'Description',
        }
    
    def clean_name(self):
        """
        Validate that Division Name contains only alphabets and spaces.
        """
        name = self.cleaned_data.get('name')
        if name:
            # Remove leading/trailing spaces for validation
            name = name.strip()
            if not re.match(r'^[A-Za-z\s]+$', name):
                raise forms.ValidationError('Only alphabets and spaces are allowed')
            # Check if it's not just spaces
            if not name.replace(' ', ''):
                raise forms.ValidationError('Division name cannot be empty or contain only spaces')
        return name
    
    def clean_location(self):
        """
        Validate that Location contains only alphabets and spaces.
        """
        location = self.cleaned_data.get('location')
        if location:
            # Remove leading/trailing spaces for validation
            location = location.strip()
            if not re.match(r'^[A-Za-z\s]+$', location):
                raise forms.ValidationError('Only alphabets and spaces are allowed')
        return location

class ForestStationForm(forms.ModelForm):
    """
    Form for adding/editing Forest Stations with validation.
    """
    class Meta:
        model = ForestStation
        fields = ['division', 'name', 'contact_number', 'address']
        widgets = {
            'division': forms.Select(attrs={
                'class': 'form-select',
                'required': True
            }),
            'name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'e.g., Nilambur Station',
                'pattern': '[A-Za-z\\s]+',
                'title': 'Only alphabets and spaces are allowed'
            }),
            'contact_number': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'e.g., 9876543210',
                'pattern': '\\d{10}',
                'maxlength': '10',
                'title': 'Must be exactly 10 digits'
            }),
            'address': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Enter full address'
            }),
        }
        labels = {
            'division': 'Forest Division *',
            'name': 'Station Name *',
            'contact_number': 'Contact Number *',
            'address': 'Address *',
        }

    def clean_name(self):
        name = self.cleaned_data.get('name')
        if name:
            name = name.strip()
            if not re.match(r'^[A-Za-z\s]+$', name):
                raise forms.ValidationError('Only alphabets and spaces are allowed')
            if not name.replace(' ', ''):
                 raise forms.ValidationError('Station name cannot be empty')
        return name

    def clean_contact_number(self):
        number = self.cleaned_data.get('contact_number')
        if number:
            if not re.match(r'^\d{10}$', number):
                raise forms.ValidationError('Contact number must be exactly 10 digits')
        return number

class AnimalForm(forms.ModelForm):
    """
    Form for adding/editing Animals.
    """
    class Meta:
        model = Animal
        fields = ['name', 'scientific_name', 'description', 'image', 'is_dangerous']
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'form-control',
                'required': True,
                'pattern': '[A-Za-z\\s]+',
                'title': 'Only alphabets and spaces are allowed'
            }),
            'scientific_name': forms.TextInput(attrs={
                'class': 'form-control',
                'pattern': '[A-Za-z\\s]+',
                'title': 'Only alphabets and spaces are allowed'
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 4,
                'required': True
            }),
            'image': forms.FileInput(attrs={'class': 'form-control', 'accept': 'image/*'}),
            'is_dangerous': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }
        labels = {
            'name': 'Animal Name *',
            'scientific_name': 'Scientific Name',
            'description': 'Description *',
            'image': 'Image',
            'is_dangerous': 'Mark as Dangerous',
        }

    def clean_name(self):
        """Validate that Animal Name contains only alphabets and spaces and is unique."""
        name = self.cleaned_data.get('name')
        if name:
            name = name.strip()
            if not re.match(r'^[A-Za-z\s]+$', name):
                raise forms.ValidationError('Only alphabets and spaces are allowed')
            if not name.replace(' ', ''):
                raise forms.ValidationError('Animal name cannot be empty or contain only spaces')
            
            qs = Animal.objects.filter(name__iexact=name)
            if self.instance and self.instance.pk:
                qs = qs.exclude(pk=self.instance.pk)
            if qs.exists():
                raise forms.ValidationError(f'An animal with the name "{name}" already exists.')
        return name

    def clean_scientific_name(self):
        """Validate that Scientific Name contains only alphabets and spaces and is unique."""
        scientific_name = self.cleaned_data.get('scientific_name')
        if scientific_name:
            scientific_name = scientific_name.strip()
            if not re.match(r'^[A-Za-z\s]+$', scientific_name):
                raise forms.ValidationError('Only alphabets and spaces are allowed')
            
            qs = Animal.objects.filter(scientific_name__iexact=scientific_name)
            if self.instance and self.instance.pk:
                qs = qs.exclude(pk=self.instance.pk)
            if qs.exists():
                raise forms.ValidationError(f'An animal with the scientific name "{scientific_name}" already exists.')
        return scientific_name

    def clean_description(self):
        """Validate that Description contains at least one alphabetic character."""
        description = self.cleaned_data.get('description')
        if description:
            # Check if it contains at least one alphabetic character
            if not re.search(r'[a-zA-Z]', description):
                raise forms.ValidationError("Description must contain alphabetic characters. Numbers alone are not allowed.")
        return description

class PreservedAnimalForm(forms.ModelForm):
    """
    Form for adding/editing Preserved Animals.
    """
    class Meta:
        model = PreservedAnimal
        fields = ['animal', 'preservation_status', 'threat_level', 'population_estimate', 'conservation_notes']
        widgets = {
            'animal': forms.Select(attrs={'class': 'form-select', 'required': True}),
            'preservation_status': forms.Select(attrs={'class': 'form-select'}),
            'threat_level': forms.Select(attrs={'class': 'form-select'}),
            'population_estimate': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': '0',
                'max': '999999',
                'placeholder': 'e.g., 150 (Max: 999999)'
            }),
            'conservation_notes': forms.Textarea(attrs={'class': 'form-control', 'rows': 4}),
        }
        labels = {
            'animal': 'Select Animal *',
            'preservation_status': 'Preservation Status *',
            'threat_level': 'Threat Level *',
            'population_estimate': 'Population Estimate',
            'conservation_notes': 'Conservation Notes',
        }
    
    def clean_population_estimate(self):
        estimate = self.cleaned_data.get('population_estimate')
        if estimate is not None:
             if estimate < 0:
                 raise forms.ValidationError("Population estimate cannot be negative.")
             if estimate > 999999:
                 raise forms.ValidationError("Population estimate must be a numeric value with a maximum of 6 digits.")
        return estimate

class ForestOfficerForm(forms.Form):
    """
    Form for adding Forest Officers with strict validation.
    """
    username = forms.CharField(
        max_length=150,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'pattern': '[A-Za-z]+',
            'title': 'Only alphabets are allowed (no spaces, numbers, or special characters)'
        }),
        label='Username *'
    )
    
    email = forms.CharField(
        widget=forms.EmailInput(attrs={
            'class': 'form-control',
            'id': 'id_email',
            'placeholder': 'officer@forest.gov'
        }),
        label='Email *',
        validators=[
            RegexValidator(
                regex=r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$',
                message='Please enter a valid email address with a proper domain extension (e.g. .com, .gov)'
            )
        ]
    )
    
    password = forms.CharField(
        min_length=8,
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Min 8 chars, 1 uppercase, 1 lowercase, 1 digit, 1 special char'
        }),
        label='Password *'
    )
    
    phone_number = forms.CharField(
        max_length=10,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'pattern': '\\d{10}',
            'maxlength': '10',
            'placeholder': 'e.g., 9876543210'
        }),
        label='Phone Number *'
    )
    
    station = forms.ModelChoiceField(
        queryset=None,  # Will be set in __init__
        required=False,
        widget=forms.Select(attrs={'class': 'form-select'}),
        label='Assign to Station'
    )
    
    designation = forms.CharField(
        max_length=100,
        widget=forms.TextInput(attrs={'class': 'form-control'}),
        label='Designation *'
    )
    
    badge_number = forms.CharField(
        max_length=50,
        widget=forms.TextInput(attrs={'class': 'form-control'}),
        label='Badge Number *'
    )
    
    def __init__(self, *args, **kwargs):
        from .models import ForestStation
        super().__init__(*args, **kwargs)
        self.fields['station'].queryset = ForestStation.objects.all()
    
    def clean_email(self):
        email = self.cleaned_data.get('email')
        if email:
            # Strict regex for email with domain extension (e.g., .com, .gov)
            email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
            if not re.match(email_pattern, email):
                raise forms.ValidationError('Please enter a valid email address with a proper domain (e.g., .com, .gov)')
        return email

    def clean_username(self):
        """Validate username contains only alphabets (no spaces, numbers, special chars)."""
        username = self.cleaned_data.get('username')
        if username:
            if not re.match(r'^[A-Za-z]+$', username):
                raise forms.ValidationError('Username must contain only alphabets (no spaces, numbers, or special characters)')
        return username
    
    def clean_password(self):
        """Validate password strength: min 8 chars, 1 uppercase, 1 lowercase, 1 digit, 1 special char."""
        password = self.cleaned_data.get('password')
        if password:
            if len(password) < 8:
                raise forms.ValidationError('Password must be at least 8 characters long')
            
            if not re.search(r'[A-Z]', password):
                raise forms.ValidationError('Password must contain at least one uppercase letter')
            
            if not re.search(r'[a-z]', password):
                raise forms.ValidationError('Password must contain at least one lowercase letter')
            
            if not re.search(r'[0-9]', password):
                raise forms.ValidationError('Password must contain at least one digit')
            
            if not re.search(r'[!@#$%^&*]', password):
                raise forms.ValidationError('Password must contain at least one special character (!@#$%^&*)')
        
        return password
    
    def clean_phone_number(self):
        """Validate phone number is exactly 10 digits."""
        phone = self.cleaned_data.get('phone_number')
        if phone:
            if not re.match(r'^\d{10}$', phone):
                raise forms.ValidationError('Phone number must be exactly 10 digits')
        return phone

class ForestOfficerEditForm(forms.Form):
    """
    Form for editing Forest Officers with strict validation.
    """
    username = forms.CharField(
        max_length=150,
        widget=forms.TextInput(attrs={'class': 'form-control'}),
        label='Username *'
    )
    
    email = forms.CharField(
        widget=forms.EmailInput(attrs={'class': 'form-control', 'id': 'email'}),
        label='Email *',
        validators=[
            RegexValidator(
                regex=r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$',
                message='Please enter a valid email address with a proper domain extension (e.g. .com, .gov)'
            )
        ]
    )
    
    phone_number = forms.CharField(
        max_length=10,
        widget=forms.TextInput(attrs={'class': 'form-control', 'id': 'phone_number'}),
        label='Phone Number *',
        validators=[
            RegexValidator(
                regex=r'^\d{10}$',
                message='Phone number must be exactly 10 digits'
            )
        ]
    )
    
    station = forms.ModelChoiceField(
        queryset=None,
        required=False,
        widget=forms.Select(attrs={'class': 'form-select', 'id': 'station'}),
        label='Assign to Station'
    )
    
    designation = forms.CharField(
        max_length=100,
        widget=forms.TextInput(attrs={'class': 'form-control', 'id': 'designation'}),
        label='Designation *'
    )
    
    badge_number = forms.CharField(
        max_length=50,
        widget=forms.TextInput(attrs={'class': 'form-control', 'id': 'badge_number'}),
        label='Badge Number *'
    )
    
    def __init__(self, *args, **kwargs):
        from .models import ForestStation
        super().__init__(*args, **kwargs)
        self.fields['station'].queryset = ForestStation.objects.all()

    def clean_username(self):
        username = self.cleaned_data.get('username')
        if username and not re.match(r'^[A-Za-z]+$', username):
            raise forms.ValidationError('Username must contain only alphabets (no spaces, numbers, or special characters)')
        return username

    # clean_email and clean_phone_number are now handled by RegexValidator
