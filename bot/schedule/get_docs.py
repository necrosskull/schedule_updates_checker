from rtu_schedule_parser.downloader import ScheduleDownloader
from rtu_schedule_parser import ExcelScheduleParser, ScheduleData
from rtu_schedule_parser.constants import Institute, Degree, ScheduleType
import pickle

import os


def load_saved_documents():
    try:
        with open(os.path.join(os.path.dirname(__file__), "saved_documents.pkl"), "rb") as file:
            return pickle.load(file)
    except FileNotFoundError:
        return []


def fetch_docs():
    downloader = ScheduleDownloader()
    saved_documents = load_saved_documents()
    new_documents = downloader.get_documents(specific_degrees={Degree.BACHELOR, Degree.MASTER})

    with open(os.path.join(os.path.dirname(__file__), "saved_documents.pkl"), "wb") as file:
        pickle.dump(new_documents, file)

    new_docs = []
    for doc in new_documents:
        if doc not in saved_documents:
            new_docs.append(doc)

    return new_docs


def get_new_docs():
    new_docs = fetch_docs()

    if len(new_docs) < 1:
        return None
    else:
        return new_docs
