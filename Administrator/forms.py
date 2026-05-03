from django import forms
from .models import Skill

class SkillForm(forms.ModelForm):
    class Meta:
        model = Skill
        fields = ['skill_name']
        

    # def clean_skill_name(self):
    #     skill_name = self.cleaned_data.get('skill_name')
        
    #     if skill_name:
    #         skill_name = skill_name.strip()
        
    #     return skill_name