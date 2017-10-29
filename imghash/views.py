from django.shortcuts import render_to_response
from django.views.decorators.csrf import csrf_exempt
from scipy.misc import imread
from imghash.hashutil import query_image
import os
from imghash.models import ImageLabel
from imghash.hashutil import hash_method_dict

# Create your views here.
def home(request):
    if (not hasattr(home,"cached_labels")):
        setattr(home,"cached_labels",[l.name for l in ImageLabel.objects.all()])
    all_radius = range(5)
    all_methods = hash_method_dict.keys()
    return render_to_response("index.html",{"all_labels":getattr(home,"cached_labels"),
                                            "all_radius":all_radius,"all_methods":all_methods})


def handle_uploaded_file(f,temp_file_path):
    if (not os.path.exists(temp_file_path)):
        open(temp_file_path,"w").write("")
    with open(temp_file_path, 'wb+') as destination:
        for chunk in f.chunks():
            destination.write(chunk)

@csrf_exempt
def handle_image_query(request):
    # process data
    temp_file_name = "temp.jpeg"
    temp_file_path = os.path.join(os.path.dirname(os.path.abspath(__file__)),'temp',temp_file_name)
    handle_uploaded_file(request.FILES['image_input'],temp_file_path)
    img_class = request.POST.get("class","back_pack")
    method_name = request.POST.get("method","Nontransfer_Latent_Hash")
    radius = int(request.POST.get("radius",2))
    # get selected domains
    domains = ["amazon","dslr","webcam"]
    selected_domains = []
    for d in domains:
        if ("domain-{}".format(d) in request.POST.keys()):
            selected_domains.append(d)
    # query image
    img = imread(temp_file_path)
    result_dict,overall_precision,overall_recall = query_image(img=img, label=img_class, method_name=method_name, radius=radius,domains=selected_domains)
    return render_to_response("query-result.html", {"result_dict":result_dict,"method":method_name,
                            "query_img":temp_file_name,"query_class":img_class,"radius":radius,"overall_precision":overall_precision,
                                                    "overall_recall":overall_recall,"selected_domains":",".join(selected_domains)})