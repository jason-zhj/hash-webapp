import sys,os,django

sys.path.extend(['F:/Project/hash-webapp/webapp'])
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "webapp.settings")
django.setup()

import itertools
from imghash.models import NonTransferLatentHashCode, Image, ImageLabel
from imghash.hashmodel.hashgen import get_hash

hash_method_dict = {
    "Nontransfer_Latent_Hash": {"table":NonTransferLatentHashCode,"function":None}
}

def hash(img,method_name):
    "return a string, containing 0 and 1"
    hashes = get_hash(method_name=method_name,images=[img])
    return hashes[0]

def compute_dist_hash(hashcode,dist):
    "`hashcode` should only contain '0' and '1', return a list of hash strings, whose hamming distance to `hashcode` is `dist`"
    hash_ls = []
    invert = lambda x:"1" if x=="0" else "0"
    code_length = len(hashcode)
    for positions in itertools.combinations(range(code_length),dist):
        # invert the hash bit at `positions`
        computed_code = "".join([invert(hashcode[i]) if i in positions else hashcode[i]
                                 for i in range(code_length)])
        hash_ls.append(computed_code)

    return hash_ls

def query_hash(hashcode,dist,method_name,domains=None):
    "return list of models.Image with hamming distance = dist"
    hash_codes_to_retrieve = compute_dist_hash(hashcode=hashcode,dist=dist)
    query_results = []
    for code in hash_codes_to_retrieve:
        # query DB to get images whose hash code == code
        table = hash_method_dict[method_name]["table"]
        hashcode_objs = table.objects.filter(code=code)
        retrieved_imgs = [obj.image for obj in hashcode_objs]
        if (domains): # filter domain selection
            retrieved_imgs = [img for img in retrieved_imgs if img.domain in domains]

        query_results += retrieved_imgs
    return query_results

def query_image(img, radius, label, method_name, domains):
    "return a dict {dist:[list of images]} and overall precision, overall recall"
    query_hash_code = hash(img,method_name)
    return_dict = {}
    total_retrieved = 0
    overall_precision = 0
    overall_recall = 0
    # total number of images in DB that have `label`
    total_img_num = ImageLabel.objects.get(name=label).get_image_num(domains=domains)
    for i in range(radius+1):
        retrieved_imgs = query_hash(hashcode=query_hash_code, dist=i, method_name=method_name, domains=domains)
        if (len(retrieved_imgs)==0):
            return_dict[i] = {"precision":0,"list":[],"recall":0}
        else:
            correct = [True if item.label.name == label else False for item in retrieved_imgs]
            precision = correct.count(True) * 1.0 / len(correct)
            recall = correct.count(True) * 1.0  / total_img_num
            overall_recall += recall
            overall_precision += precision * len(retrieved_imgs)
            total_retrieved += len(retrieved_imgs)
            # list of [Image,boolean]
            img_and_correct = [[retrieved_imgs[i],correct[i]] for i in range(len(retrieved_imgs))]
            return_dict[i] = {"precision":precision,"list":img_and_correct,"recall":recall}

    if (total_retrieved > 0): # otherwise over_precision will be zero
        overall_precision /= float(total_retrieved)
    return return_dict,overall_precision, overall_recall

if __name__ == "__main__":
    print(compute_dist_hash(hashcode="010101",dist=2))