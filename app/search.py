from flask import current_app


def add_to_index(index, model) -> None:
    """Add a model to the search index.
    :param index: The index to add to.
    :param model: The model to add.
    """
    if not current_app.elasticsearch:
        return
    payload = {}
    for field in model.__searchable__:
        payload[field] = getattr(model, field)
    current_app.elasticsearch.index(index=index, id=model.id, body=payload)


def remove_from_index(index, model) -> None:
    """Remove a model from the search index.
    :param index: The index to remove from.
    :param model: The model to remove.
    :return: None
    """
    if not current_app.elasticsearch:
        return
    current_app.elasticsearch.delete(index=index, id=model.id)


def query_index(index, query, page:int, per_page:int) -> tuple:
    """Query the search index.
    :param index: The index to search.
    :param query: The query string.
    :param page: The page number.
    :param per_page: The number of results per page.
    :return: A tuple of (ids, total), where ids is a list of ids of the
    results on the page, and total is the total number of results
    """
    if not current_app.elasticsearch:
        return [], 0
    search = current_app.elasticsearch.search(
        index=index,
        body={'query': {'multi_match': {'query': query, 'fields': ['*']}},
              'from': (page - 1) * per_page, 'size': per_page})
    ids = [int(hit['_id']) for hit in search['hits']['hits']]
    return ids, search['hits']['total']['value']
