import sys,os,django

sys.path.extend(['F:/Project/hash-webapp/webapp'])
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "webapp.settings")
django.setup()

from imghash.models import Image,ImageLabel,NonTransferLatentHashCode
from django.db.transaction import atomic

@atomic
def import_image_label():
    labels = ['back_pack', 'bike', 'bike_helmet', 'bookcase', 'bottle', 'calculator', 'desktop_computer', 'desk_chair',
               'desk_lamp', 'file_cabinet', 'headphones', 'keyboard'
        , 'laptop_computer', 'letter_tray', 'mobile_phone', 'monitor', 'mouse', 'mug', 'paper_notebook', 'pen', 'phone',
               'printer', 'projector', 'punchers', 'ring_binder', 'ruler', 'scissors', 'speaker', 'stapler',
               'tape_dispenser', 'trash_can']
    for label in labels:
        ImageLabel.objects.create(
            name = label
        )

def get_image_domain(filename):
    if (filename.find("amazon")==0):
        return "amazon"
    elif (filename.find("webcam")==0):
        return "webcam"
    elif (filename.find("dslr") == 0):
        return "dslr"
    raise Exception("No valid domain for {}".format(filename))

@atomic
def import_image(data_path):
    "import data into Image, here assume the images are organized in folders named using the image class label"
    for dirname in os.listdir(data_path):
        if os.path.isfile(os.path.join(data_path,dirname)):
           continue

        label = dirname
        imagelabel = ImageLabel.objects.get(name=label)
        sub_path = os.path.join(data_path,dirname)
        for filename in [f for f in os.listdir(sub_path) if os.path.isfile(os.path.join(sub_path,f))]:
            Image.objects.create(
                file_path = os.path.join(sub_path,filename),
                label = imagelabel,
                domain = get_image_domain(filename)
            )
            print("{}/{} is imported".format(dirname,filename))

def clean_hash_code(code):
    "return a code 0/1 string w/o space"
    return code.strip().replace(" ","")

def import_single_hash(filename,label,hashcode,model):
    "import a single entry to `model`"
    if (not hasattr(import_single_hash,"images")):
        setattr(import_single_hash,"images",Image.objects.all())
    img = [image for image in import_single_hash.images if image.file_path.find(filename)!=-1 and image.label.name == label]
    assert len(img) == 1
    model.objects.create(
        image = img[0],
        code = clean_hash_code(hashcode)
    )

@atomic
def import_image_hash(hash_file,model_class):
    "hash_file should be in csv format ['file','class','hash'], with first line being the title"
    with open(hash_file,"r") as f:
        lines = f.readlines()[1:]
        for line in lines:
            filename,label,hashcode = line.strip().split(",")
            import_single_hash(filename,label,hashcode,model=model_class)
    print("import finished")

if __name__ == "__main__":
    # import_image(data_path="F:/data/domain_adaptation_images/all-in-one")
    NonTransferLatentHashCode.objects.all().delete()
    import_image_hash(hash_file="F:/Project/keras-test/results/latest-hash.csv",model_class=NonTransferLatentHashCode)