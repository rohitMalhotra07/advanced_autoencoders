# AUTOGENERATED! DO NOT EDIT! File to edit: ../nbs/inference_pipeline.ipynb.

# %% auto 0
__all__ = ['get_test_data_loader', 'load_model', 'generate_embeddings_df', 'save_data', 'generate_embedding_mae_pipeline',
           'generate_embedding_vqvae_pipeline']

# %% ../nbs/inference_pipeline.ipynb 2
import numpy as np
import pandas as pd
import torch
from torch.utils.data import DataLoader
from tqdm import tqdm

from .config import ConfigMaeLarge, ConfigVQVAE
from .dataset import MyImageDataset
from advanced_autoencoders.models import (
    get_embeddings_mae,
    get_embeddings_vae,
    get_mae_model,
    get_vae_model,
)
from advanced_autoencoders.utils import (
    get_test_transforms,
    make_images_dataframe,
    seed_everything,
)

# %% ../nbs/inference_pipeline.ipynb 5
def get_test_data_loader(df, cnfg):
    dataset = MyImageDataset(df, augmentations=get_test_transforms(cnfg))
    dl = DataLoader(dataset, batch_size=32, shuffle=False)

    return dl

# %% ../nbs/inference_pipeline.ipynb 6
def load_model(cnfg, model):
    model.load_state_dict(torch.load(f"{cnfg.MODELS_DIR}{cnfg.model_name}.bin"))
    model.cuda()
    model.eval()

    return model

# %% ../nbs/inference_pipeline.ipynb 8
def generate_embeddings_df(cnfg, model, dl, embd_name, get_embd_fnc):
    all_embeddings = []
    with torch.no_grad():
        for i, samples in enumerate(tqdm(dl)):
            embeddings = get_embd_fnc(model, samples.cuda())
            # embeddings = torch.flatten(encoded, start_dim=1).cpu().numpy()
            all_embeddings.extend(embeddings)

    final_df = pd.DataFrame(
        data=np.array(all_embeddings),
        columns=cnfg.EMBEDDING_COL_NAMES,
    )
    final_df[embd_name] = new_df[embd_name].values

    return final_df

# %% ../nbs/inference_pipeline.ipynb 9
def save_data(df, cnfg):
    df.to_csv(cnfg.EMBEDDING_FILE_PATH, index=False)

# %% ../nbs/inference_pipeline.ipynb 11
def generate_embedding_mae_pipeline():
    CONFIG = ConfigMaeLarge()
    seed_everything(seed=CONFIG.seed)
    df_all = make_images_dataframe(CONFIG)
    print(df_all.shape, df_all.image_name.unique().size)
    dl = get_test_data_loader(df_all, CONFIG)
    model = get_mae_model(cnfg)
    model = load_model(CONFIG, model)

    final_df = generate_embeddings_df(CONFIG, model, dl, "mae_emb", get_embeddings_mae)

    save_data(final_df, CONFIG)
    return

# %% ../nbs/inference_pipeline.ipynb 13
def generate_embedding_vqvae_pipeline():
    CONFIG = ConfigVQVAE()
    seed_everything(seed=CONFIG.seed)
    df_all = make_images_dataframe(CONFIG)
    print(df_all.shape, df_all.image_name.unique().size)
    dl = get_test_data_loader(df_all, CONFIG)
    model = get_vae_model(cnfg)
    model = load_model(CONFIG, model)

    final_df = generate_embeddings_df(CONFIG, model, dl, "vae_emb", get_embeddings_vae)

    save_data(final_df, CONFIG)
    return
