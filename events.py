from llama_index.core.workflow import Event

class RetrieveEvent(Event):
    pass


class RetrievedNodesEvent(Event):
    nodes: list


class FilteredNodesEvent(Event):
    nodes: list


class NoResultsEvent(Event):
    message: str


class AnswerEvent(Event):
    answer: str


class RouterEvent(Event):
    pass

class StructuredAnswerEvent(Event):
    answer: str