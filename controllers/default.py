# -*- coding: utf-8 -*-
# this file is released under public domain and you can use without limitations

#########################################################################
## This is a sample controller
## - index is the default action of any application
## - user is required for authentication and authorization
## - download is for downloading files uploaded in the db (does streaming)
#########################################################################

def index():
    """
    example action using the internationalization operator T and flash
    rendered by views/default/index.html or views/generic.html

    if you need a simple wiki simply replace the two lines below with:
    return auth.wiki()
    """

    #rows = db(db.courses.course_name != None).select()

    db_courses = db(db.courses.course_name != None).select()

    my_courses = []

    courses = []
    for db_course in db_courses:
        db_groups = db(db.groups.course_id == db_course.course_number).select()
        tirguls = []
        lectures = []
        for db_group in db_groups:
            db_moeds = db(db.moed.group_id == db_group.grouop_id).select()
            moeds = []
            for db_moed in db_moeds:
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
            'lectures': lectures
        })

    print courses

    s = {'maxCid': -1, 'cands': [], 'total_points': 0}
    bt(s, courses)

    #for row in rows:
#       c = row.points
    #c = rows[0].course_name


    return dict(cc='ha')


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


needed_points = 13

def accept(s):
    print s['total_points']
    return abs(needed_points - s['total_points']) <= 2


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
def bt(c, courses):
    if reject(c, courses):
        return

    if accept(c):
        print 'Yoho! we have a timetable!'
        print c

    for c_i in range(c['maxCid'] + 1, len(courses)):
        course = courses[c_i]
        for t_i in range(len(course['tirguls'])):
            for l_i in range(len(course['lectures'])):
                bt({
                    'maxCid': c_i,
                    'cands': c['cands'] + [{'cid': c_i, 'tid': t_i, 'lid': l_i}],
                    'total_points': c['total_points'] + course['points']
                }, courses)