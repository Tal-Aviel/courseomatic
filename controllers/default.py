# -*- coding: utf-8 -*-
# this file is released under public domain and you can use without limitations

#########################################################################
## This is a sample controller
## - index is the default action of any application
## - user is required for authentication and authorization
## - download is for downloading files uploaded in the db (does streaming)
#########################################################################

needed_points = 14

def index():
    return dict()

def cal():
    return dict()

def get_courses():
    db_courses = db(db.courses.course_number != None).select()

    result = []
    for course in db_courses:
        result.append({
            "name": course.course_name,
            "course_number": course.course_number,
            "points": course.points
        })

    return response.json(result)

def timetable():
    session.userdata = request.vars
    return dict()


    #return request.vars['courses[]'][1]

def calcSys():
    """
    example action using the internationalization operator T and flash
    rendered by views/default/index.html or views/generic.html

    if you need a simple wiki simply replace the two lines below with:
    return auth.wiki()
    """

    #rows = db(db.courses.course_name != None).select()

    db_courses = db(db.courses.course_number != None).select()

    dat = session.userdata
    cs = dat['courses[]']

    courses = []
    for db_course in db_courses:

        if str(db_course.course_number) not in cs:
            #if db_course.course_number not in [67504, 67506, 67109]:
            continue

        db_groups = db(db.groups.course_id == db_course.course_number).select()
        tirguls = []
        lectures = []
        for db_group in db_groups:
            db_moeds = db(db.moed.group_id == db_group.grouop_id).select()
            moeds = []
            for db_moed in db_moeds:
                if str(db_moed.week_day) not in dat['days[]']:
                    continue
                moeds.append({
                    's': db_moed.hour_from,
                    'e': db_moed.hour_to,
                    'd': db_moed.week_day
                })
            if db_group.lesson_type == 'lesson':
                lectures = lectures + [moeds]
            else:
                tirguls = tirguls + [moeds]
        courses.append({
            'course_number': db_course.course_number,
            'points': db_course.points,
            'semester': db_course.semester,
            'tirguls' : tirguls,
            'lectures': lectures,
            'course_name': db_course.course_name
        })

    s = {'maxCid': -1, 'cands': [], 'total_points': 0}
    result = []
    bt(s, courses, result)

    #print result

    #for row in rows:
#       c = row.points
    #c = rows[0].course_name

    print 'found'
    print len(result)

    ext = []

    for j in range(0, min(5, len(result))):
        r = result[j]
        hours = {}
        for i in range(20):
            hours[i] = {}

        for cand in r['cands']:
            course = courses[cand['cid']]
            tir = course['tirguls'][cand['tid']]
            lec = course['lectures'][cand['lid']]
            both = tir + lec
            # for show in both:
            #     for i in range(show['s'], show['e']):
            #         hours[i][show['d']] = {
            #             'name': course['course_name'],
            #             'lesson_type': 'lesson' }
            for show in tir:
                for i in range(show['s'], show['e']):
                    hours[i][show['d']] = {
                        'name': course['course_name'],
                        'lesson_type': 'tirgul',
                        'points': course['points']}
            for show in lec:
                for i in range(show['s'], show['e']):
                    hours[i][show['d']] = {
                        'name': course['course_name'],
                        'lesson_type': 'lesson',
                        'points': course['points']}
        ext.append(hours)



#    return dict(cc=hours)
    return response.json(ext)


def user():
    """
    exposes:
    http://..../[app]/default/user/login
    http://..../[app]/default/user/logout
    http://..../[app]/default/user/register
    http://..../[app]/default/user/profile
    http://..../[app]/default/user/retrieve_password
    http://..../[app]/default/user/change_password
    http://..../[app]/default/user/manage_users (requires membership in
    use @auth.requires_login()
        @auth.requires_membership('group name')
        @auth.requires_permission('read','table name',record_id)
    to decorate functions that need access control
    """
    return dict(form=auth())


@cache.action()
def download():
    """
    allows downloading of uploaded files
    http://..../[app]/default/download/[filename]
    """
    return response.download(request, db)


def call():
    """
    exposes services. for example:
    http://..../[app]/default/call/jsonrpc
    decorate with @services.jsonrpc the functions to expose
    supports xml, json, xmlrpc, jsonrpc, amfrpc, rss, csv
    """
    return service()






def reject(c, courses):
    for a in range(0, len(c['cands'])):
        for b in range(0, len(c['cands'])):
            if a == b:
                continue
            candsa = c['cands'][a]
            candsb = c['cands'][b]

            coursea = courses[candsa['cid']]
            courseb = courses[candsb['cid']]

            ta = coursea['tirguls'][candsa['tid']]
            tb = courseb['tirguls'][candsb['tid']]

            la = coursea['lectures'][candsa['lid']]
            lb = courseb['lectures'][candsb['lid']]

            aselection = ta + la
            bselection = tb + lb

            for aitem in aselection:
                for bitem in bselection:
                    if intersect(aitem, bitem):
                        return True

    return False


def accept(s):
    return abs(int(session.userdata['points']) - s['total_points']) <= 2


def intersect(a, b):
    return (a['d'] == b['d']) and intersect_inner(a['s'], a['e'], b['s'], b['e'])


def intersect_inner(s1, e1, s2, e2):
    if (s2 >= s1) and (s2 < e1):
        return True
    if (e2 > s1) and (e2 <= e1):
        return True
    if (s2 <= s1) and (e2 > e1):
        return True
    return False


# c.maxCid
# cid, tid, total_points
def bt(c, courses, result):
    if reject(c, courses):
        return

    if accept(c):
        result.append(c)
        if len(result) == 2:
            return

    for c_i in range(c['maxCid'] + 1, len(courses)):
        course = courses[c_i]
        for t_i in range(len(course['tirguls'])):
            for l_i in range(len(course['lectures'])):
                bt({
                    'maxCid': c_i,
                    'cands': c['cands'] + [{'cid': c_i, 'tid': t_i, 'lid': l_i}],
                    'total_points': c['total_points'] + course['points']
                }, courses, result)