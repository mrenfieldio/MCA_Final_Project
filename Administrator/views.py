from django.shortcuts import redirect, render
from .forms import SkillForm

# Create your views here.
def ManageSkill(request):
    context={}
    frm=SkillForm(request.POST or None)
    if frm.is_valid():
        frm.save()
        return redirect('manage_skill')
    context['form']=frm
    return render(request, 'administrator/manage_skill.html', context)