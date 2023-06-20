from django.shortcuts import render
from django.http import HttpResponse
from joblib import load
model = load('SavedModels\model.joblib')
# Create your views here.


def FinalResults(request):

    if request.method == 'POST':

        country = request.POST['country'],  
        region = request.POST['region'],  
        duration = request.POST['duration'],  
        city = request.POST['city'],  
        multiple = request.POST['multiple'],  f
        attack_type = request.POST['attack_type'],  
        target_type = request.POST['target_type'],                                  
        weapon = request.POST['weapon'],  
        kid_hostage = request.POST['kid_hostage'],  
        group = request.POST['group'],  

        vars = [country,region, duration, city , multiple, attack_type  , target_type , weapon , kid_hostage , group]

        pred = model.predict([vars])
        
        if pred == 1:
            pred = 'Succesful'
        elif pred == 0:
            pred = "Unsucceful"
        else:
            print('hii')
        
        return render(request , 'index.html', {'results' : pred})
    return render(request , 'index.html')