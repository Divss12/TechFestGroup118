import os
import random
import sys
from typing import Sequence, Mapping, Any, Union
import torch


def get_value_at_index(obj: Union[Sequence, Mapping], index: int) -> Any:
    """Returns the value at the given index of a sequence or mapping.

    If the object is a sequence (like list or string), returns the value at the given index.
    If the object is a mapping (like a dictionary), returns the value at the index-th key.

    Some return a dictionary, in these cases, we look for the "results" key

    Args:
        obj (Union[Sequence, Mapping]): The object to retrieve the value from.
        index (int): The index of the value to retrieve.

    Returns:
        Any: The value at the given index.

    Raises:
        IndexError: If the index is out of bounds for the object and the object is not a mapping.
    """
    try:
        return obj[index]
    except KeyError:
        return obj["result"][index]


def find_path(name: str, path: str = None) -> str:
    """
    Recursively looks at parent folders starting from the given path until it finds the given name.
    Returns the path as a Path object if found, or None otherwise.
    """
    # If no path is given, use the current working directory
    if path is None:
        path = os.getcwd()

    # Check if the current directory contains the name
    if name in os.listdir(path):
        path_name = os.path.join(path, name)
        print(f"{name} found: {path_name}")
        return path_name

    # Get the parent directory
    parent_directory = os.path.dirname(path)

    # If the parent directory is the same as the current directory, we've reached the root and stop the search
    if parent_directory == path:
        return None

    # Recursively call the function with the parent directory
    return find_path(name, parent_directory)


def add_comfyui_directory_to_sys_path() -> None:
    """
    Add 'ComfyUI' to the sys.path
    """
    comfyui_path = find_path("ComfyUI")
    if comfyui_path is not None and os.path.isdir(comfyui_path):
        sys.path.append(comfyui_path)
        print(f"'{comfyui_path}' added to sys.path")


def add_extra_model_paths() -> None:
    """
    Parse the optional extra_model_paths.yaml file and add the parsed paths to the sys.path.
    """
    from main import load_extra_path_config

    extra_model_paths = find_path("extra_model_paths.yaml")

    if extra_model_paths is not None:
        load_extra_path_config(extra_model_paths)
    else:
        print("Could not find the extra_model_paths config file.")


add_comfyui_directory_to_sys_path()
add_extra_model_paths()

from nodes import (
    CheckpointLoaderSimple,
    KSampler,
    LoraLoader,
    VAEDecode,
    CLIPTextEncode,
    SaveImage,
    NODE_CLASS_MAPPINGS,
    EmptyLatentImage,
)

def gen_neutral_face(name, description, checkpointloadersimple_4, emptylatentimage, cliptextencode, ksampler, vaedecode, saveimage, seed):

    emptylatentimage_5 = emptylatentimage.generate(
        width=512, height=512, batch_size=1
    )

    cliptextencode_6 = cliptextencode.encode(
        text="face front, " + description[0],
        clip=get_value_at_index(checkpointloadersimple_4, 1),
    )

    cliptextencode_7 = cliptextencode.encode(
        text="background, text, hand" + description[1],
        clip=get_value_at_index(checkpointloadersimple_4, 1),
    )

    
    ksampler_3 = ksampler.sample(
        seed=seed,
        steps=20,
        cfg=8,
        sampler_name="euler",
        scheduler="normal",
        denoise=1,
        model=get_value_at_index(checkpointloadersimple_4, 0),
        positive=get_value_at_index(cliptextencode_6, 0),
        negative=get_value_at_index(cliptextencode_7, 0),
        latent_image=get_value_at_index(emptylatentimage_5, 0),
    )

    vaedecode_8 = vaedecode.decode(
        samples=get_value_at_index(ksampler_3, 0),
        vae=get_value_at_index(checkpointloadersimple_4, 2),
    )

    saveimage_9 = saveimage.save_images(
        filename_prefix=name+"_neutral", images=get_value_at_index(vaedecode_8, 0)
    )

def gen_lora_face(name, description, lora_name, lora_prompt, expression_name, checkpointloadersimple_4, emptylatentimage, loraloader, cliptextencode, ksampler, vaedecode, saveimage, seed):

    emptylatentimage_5 = emptylatentimage.generate(
        width=512, height=512, batch_size=1
    )

    loraloader_10 = loraloader.load_lora(
        lora_name=lora_name,
        strength_model=1,
        strength_clip=1,
        model=get_value_at_index(checkpointloadersimple_4, 0),
        clip=get_value_at_index(checkpointloadersimple_4, 1),
    )

    cliptextencode_6 = cliptextencode.encode(
        text="face front, " + lora_prompt + description[0],
        clip=get_value_at_index(loraloader_10, 1),
    )

    cliptextencode_7 = cliptextencode.encode(
        text="background, text, hand" + description[1],
        clip=get_value_at_index(loraloader_10, 1),
    )


    ksampler_3 = ksampler.sample(
        seed=seed,
        steps=20,
        cfg=8,
        sampler_name="euler",
        scheduler="normal",
        denoise=1,
        model=get_value_at_index(loraloader_10, 0),
        positive=get_value_at_index(cliptextencode_6, 0),
        negative=get_value_at_index(cliptextencode_7, 0),
        latent_image=get_value_at_index(emptylatentimage_5, 0),
    )

    vaedecode_8 = vaedecode.decode(
        samples=get_value_at_index(ksampler_3, 0),
        vae=get_value_at_index(checkpointloadersimple_4, 2),
    )

    saveimage_9 = saveimage.save_images(
        filename_prefix=name+"_"+expression_name, images=get_value_at_index(vaedecode_8, 0)
    )

def main(characters):
    with torch.inference_mode():
        checkpointloadersimple = CheckpointLoaderSimple()
        checkpointloadersimple_4 = checkpointloadersimple.load_checkpoint(
            ckpt_name="irismix_v90.safetensors"
        )

        emptylatentimage = EmptyLatentImage()

        loraloader = LoraLoader()
        cliptextencode = CLIPTextEncode()

        ksampler = KSampler()
        vaedecode = VAEDecode()
        saveimage = SaveImage()

        


        for name, description in characters.items():
            seed = random.randint(1, 2**64)    
            #generate neutral face
            gen_neutral_face(name, description, checkpointloadersimple_4, emptylatentimage, cliptextencode, ksampler, vaedecode, saveimage, seed)
            # happy
            gen_lora_face(name, description, "sensualface_type4.safetensors", "happy, smiling, ", "happy", checkpointloadersimple_4, emptylatentimage, loraloader, cliptextencode, ksampler, vaedecode, saveimage, seed)
            # smug
            gen_lora_face(name, description, "doyagao_v080.safetensors", "smug expression, ", "smug", checkpointloadersimple_4, emptylatentimage, loraloader, cliptextencode, ksampler, vaedecode, saveimage, seed)
            # angry
            gen_lora_face(name, description, "gekioko_v250.safetensors", "angry, frown,", "angry", checkpointloadersimple_4, emptylatentimage, loraloader, cliptextencode, ksampler, vaedecode, saveimage, seed)
            # worried
            gen_lora_face(name, description, "worriedeyes_v100.safetensors", "worried, scared, ", "worried", checkpointloadersimple_4, emptylatentimage, loraloader, cliptextencode, ksampler, vaedecode, saveimage, seed)
            # embarassed
            gen_lora_face(name, description, "yudedako_v100.safetensors", "embarassed, ashamed, ", "embarassed", checkpointloadersimple_4, emptylatentimage, loraloader, cliptextencode, ksampler, vaedecode, saveimage, seed)
            # heart-eye
            gen_lora_face(name, description, "hotarueye_heart1_v100.safetensors", "heart eye, happy ", "heart-eyed", checkpointloadersimple_4, emptylatentimage, loraloader, cliptextencode, ksampler, vaedecode, saveimage, seed)
            # star-eye
            gen_lora_face(name, description, "hotarueye_star1_v100.safetensors", "star eye, joyous, ", "starry-eyed", checkpointloadersimple_4, emptylatentimage, loraloader, cliptextencode, ksampler, vaedecode, saveimage, seed)
        


if __name__ == "__main__":
    import time
    t = time.time()
    characters = {
        #format:
        #name: [positive prompt/description of character, negative prompt]
        'Sorceress': ['Young sorceress, short brown hair, girl, brown eyes, purple robe', 'boy'],
        'Explorer': ['Young explorer man, short wavy blond hair, blue eyes, white shirt', 'girl']
    }
    main(characters)
    
    print("finished in", time.time() - t)
