# Helper fun

page = 3
offset = 100,
limit=50

def RenderPage(page, limit=50):
	page = 1 if page < 1 else page
	offset = (page - 1) * limit
	limit = limit + offset
	return {
		'page': page,
		'offset': offset,
		'limit': limit,
	}

def NaviPage(total=0, page=1, offset=50):

	_navi = dict()

	_page = total/offset
	if _page <= 5:
		_page_max = _page
	else:
		if page >= 4 and page < _page - 2:
			_page_max = 7
		elif page == 3  or page == _page - 2:
			_page_max = 6
		else:
			_page_max = 5
	for x in xrange(1,_page_max+1):
		_navi[x] = [x, False]

	if len(_navi) > 0:
		_navi[_page_max][0] = _page

		if _page <= 5:
			_navi[page] = [page, True]
		else:
			if page <= 2:
				_navi[page] = [page, True]
				_navi[4][0] = False
			elif page >= _page - 1:
				active = _page - page
				_navi[_page_max - active][1] = True 
				_navi[3][0] = _page - 2
				_navi[4][0] = _page - 1
				_navi[2][0] = False
			else:
				if page == 3:
					_navi[page] = [page, True]
					_navi[5][0] = False
					_navi[6][0] = _page
				elif page == _page - 2:
					_navi[5][0] = page+1
					_navi[4] = [page, True]
					_navi[3][0] = page-1
					_navi[2][0] = False
				else:
					_navi[2][0] = False
					_navi[3][0] = page - 1
					_navi[4] = [page, True]
					_navi[5][0] = page + 1
					_navi[6][0] = False

	return {
		'pageTotal': _page,
		'pageCurrent': page,
		'navi': _navi,
	}
































