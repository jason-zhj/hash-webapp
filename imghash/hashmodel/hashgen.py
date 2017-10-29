"""
For generating hash for image
"""

import tensorflow as tf
import os, time
import numpy as np
from scipy.misc import imread, imresize
from imghash.hashmodel.tfutil import load_graph
from webapp.settings import BASE_DIR

MODEL_PARAMS = {
    "Nontransfer_Latent_Hash":{
        "model_path": os.path.join(BASE_DIR,"tfmodels/nontransfer/latent-16/frozen_model.pb"),
        "output_tensor_name":"prefix/latent_set/latent_output:0",
        "image_size":[224,224]
    }
}

def _format_hash(code_ls):
    "`code_ls` is numpy array, with each element being a number, return a binary string"
    ls = code_ls.astype(int)
    ls[ls == -1] = 0
    return "".join(ls.astype(str))

#TODO: need to change this when we have multiple models
def _generate_hash(images,model_path,output_tensor_name):
    "use trained model to produce hash code for image, hash code is a binary string '01010...'"
    # cache the graph as static var
    if (not hasattr(_generate_hash,"graph")):
        setattr(_generate_hash,"graph",load_graph(model_path))

    graph = getattr(_generate_hash,"graph")
    imgs = graph.get_tensor_by_name("prefix/imgs:0") #TODO: we may remove this hardcode
    latent_output = graph.get_tensor_by_name(output_tensor_name)

    with tf.Session(graph=graph) as sess:
        start = time.time()
        sess_outputs = sess.run(latent_output, feed_dict={imgs: images})
        # hash code = sgn(output-0.5)
        results = np.sign(np.subtract(sess_outputs,0.5))
        print("Generating hash takes {} s".format(time.time() - start))
        return [_format_hash(code) for code in results]

def get_hash(images,method_name):
    "`images` is list of images read by imread, returns a list of binary strings '0101...'"
    params = MODEL_PARAMS[method_name]
    required_size = params["image_size"]
    images = [imresize(image, (required_size[0], required_size[1])) for image in images]
    return _generate_hash(images=images,model_path=params["model_path"],output_tensor_name=params["output_tensor_name"])

if __name__ == "__main__":
    img = imread("F:/data/domain_adaptation_images/all-in-one/back_pack/amazon_frame_0001.jpg")
    results = get_hash(images=[img],method_name="Nontransfer_Latent_Hash")