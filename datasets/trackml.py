from pathlib import Path
from zipfile import ZipFile
from trackml.dataset import load_dataset, load_event

import numpy as np
import pandas as pd


def _transform(hits, blacklist_hits):
    hits = hits[np.logical_not(hits.hit_id.isin(blacklist_hits.hit_id))]
    hits = hits.rename(columns={'layer_id': 'layer', 'particle_id': 'track'})
    hits.track = hits.track.where(hits.track != 0, other=-1)
    hits.reset_index(drop=True, inplace=True)
    hits['layer'] = hits.layer // 2
    return hits


def get_hits_trackml(n_events=None,
                     train_zip: Path = Path(__file__).parents[1] / 'data/trackml/train_sample.zip',
                     blacklist_zip: Path = Path(__file__).parents[1] / 'data/trackml/blacklist_training.zip',
                     ) -> pd.DataFrame:
    events = []
    with ZipFile(blacklist_zip) as bz:
        for event_id, hits, truth in load_dataset(train_zip.resolve(), nevents=n_events, parts=['hits', 'truth']):
            hits = hits.merge(truth, on='hit_id')
            with bz.open(f'event{event_id:09}-blacklist_hits.csv') as f:
                blacklist_hits = pd.read_csv(f)
            hits = _transform(hits, blacklist_hits)
            hits['event_id'] = event_id
            events.append(hits)
    return pd.concat(events, ignore_index=True)


def get_hits_trackml_one_event(path: Path = Path(__file__).parents[1] / 'data/trackml'):
    event_number = 1000
    hits, truth = load_event(path / 'event000001000', ['hits', 'truth'])
    hits = hits.merge(truth, on='hit_id')
    blacklist_hits = pd.read_csv(path / f'event{event_number:09}-blacklist_hits.csv')
    hits = _transform(hits, blacklist_hits)
    hits['event_id'] = 1000
    return hits


def get_hits_trackml_by_volume(n_events=None, *args, **kwargs):
    hits = get_hits_trackml(n_events=n_events, *args, **kwargs)
    hits.event_id = hits.event_id.astype(str) + '-' + hits.volume_id.astype(str)
    return hits if n_events is None else hits[hits.event_id.isin(hits.event_id.unique()[:n_events])]


def get_hits_trackml_one_event_by_volume():
    hits = get_hits_trackml_one_event()
    hits = hits[hits.volume_id == 7].reset_index(drop=True)
    hits.event_id = hits.event_id.astype(str) + '-' + hits.volume_id.astype(str)
    return hits
