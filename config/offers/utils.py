from urllib.parse import urlencode


def build_offers_query(search_query='', category_filter='', page=None):
    params = {}
    if search_query:
        params['search'] = search_query
    if category_filter:
        params['category'] = category_filter
    if page:
        params['page'] = page
    return urlencode(params)
