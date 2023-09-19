from rtu_schedule_parser.downloader import ScheduleDownloader
from rtu_schedule_parser import ExcelScheduleParser, ScheduleData
from rtu_schedule_parser.constants import Institute, Degree, ScheduleType
import pickle

import os

from rtu_schedule_parser.utils import Period

downloader = ScheduleDownloader()


def load_saved_documents():
    try:
        with open(os.path.join(os.path.dirname(__file__), "saved_documents.pkl"), "rb") as file:
            return pickle.load(file)
    except FileNotFoundError:
        return []


def load_schedule():
    try:
        with open(os.path.join(os.path.dirname(__file__), "schedule.pkl"), "rb") as file:
            return pickle.load(file)
    except FileNotFoundError:
        return []


def fetch_docs():
    saved_documents = load_saved_documents()
    new_documents = downloader.get_documents(specific_degrees={Degree.BACHELOR})

    with open(os.path.join(os.path.dirname(__file__), "saved_documents.pkl"), "wb") as file:
        pickle.dump(new_documents, file)

    new_docs = []
    for doc in new_documents:
        if doc not in saved_documents:
            new_docs.append(doc)

    saved_documents.clear()
    new_documents.clear()
    return new_docs


def download_docs():
    docs = downloader.get_documents(specific_degrees={Degree.BACHELOR})

    downloaded = downloader.download_all(docs)

    saved_schedule = load_schedule()

    # folder_path = os.path.dirname(__file__)
    # folder_path = os.path.join(folder_path, "toparse")
    # print(folder_path)
    #
    # downloaded = [f for f in os.listdir(folder_path) if f.endswith(".xlsx")]

    schedule = []
    for doc in downloaded:
        # file_path = os.path.join(folder_path, doc)

        parser = ExcelScheduleParser(
            doc[1], doc[0].period, doc[0].institute, doc[0].degree
        )

        # parser = ExcelScheduleParser(
        #     file_path, Period(2021, 2022, 2), Institute.IIT, Degree.BACHELOR
        # )

        if schedule is None:
            schedule = parser.parse(force=True)
        else:
            schedule.extend(parser.parse(force=True).get_schedule())

    with open(os.path.join(os.path.dirname(__file__), "schedule.pkl"), "wb") as file:
        pickle.dump(schedule, file)

    new_schedule = []
    for group in schedule:
        if group not in saved_schedule:
            new_schedule.append(group)

    groups_by_institute = {}
    for group in new_schedule:
        institute = group.institute.short_name
        group_name = group.group

        if institute not in groups_by_institute:
            groups_by_institute[institute] = []

            # Добавляем группу к соответствующему институту
        groups_by_institute[institute].append(group_name)

    saved_schedule.clear()
    new_schedule.clear()

    return groups_by_institute


def get_new_docs():
    new_docs = fetch_docs()

    if len(new_docs) < 1:
        return None
    else:
        return new_docs
