from server import db
from server import pcalc

class bot:
    def __init__(self):
        self.name = 'Users management'
        return
    def run_bot(self, request, vntid, token, url):
        #print("users management bot is running")
        #
        print("message for process=", request)
        """
        message for process= {
            'reqid': 2,
            'cur_uservntid': 5,
            'cur_name': 'users',
            'src_uservntid': 1,
            'src_name': 'rom',
            'which_dst': 2,
            'dst_uservntid': None,
            'dst_name': '',
            'dst_presvcid': None,
            'dst_presvc_name': '',
            'dst_svcid': 4,
            'dst_svc_name': 'admin.users',
            'subject': 'test request for new user testuser2',
            'comment': 'descr test request for new user',
            'created': datetime.datetime(2020, 6, 18, 12, 24, 4),
            'changed': datetime.datetime(2020, 6, 18, 12, 24, 5),
            'action': 'Requested',
            'operation': 'createnewuser',
            'storage': '',
            'formid': 0,
            'formbody_json': [
                {'name': 'user nickname', 'value': 'testuser2'},
                {'name': 'groupname', 'value': 'test2'},
                {'name': 'user new nickname', 'value': ''},
                {'name': 'service name', 'value': ''}
            ]
        }
        """
        source_uservntid = request['src_uservntid']
        cur_uservntid = request['cur_uservntid']
        reqid = request['reqid']
        data = {}
        nickname = ''
        message = 'Checked by Users Bot'
        # ====== Create New User ======
        if request['operation'] == 'createnewuser':
            nickname = ''
            groupname = ''
            #email = None
            for i in request['formbody_json']:
                if i['name'] == 'user nickname':
                    nickname = i['value']
                if i['name'] == 'groupname':
                    groupname = i['value']
                #if i['name'] == 'email':
                #    if i['value']:
                #        email = i['value']
            # create new user
            #
            # add nickname to vnt
            #uservntid = db.db_uservnt_new(vntid, userid, nickname)
            # add nickname to "adm" group
            #grpusrid = db.db_grpusr_new(groupid, uservntid)
            #
            # !!!! we can't create new user here - we need to generate hash password
            # send it back to user
            # user will deliver it in invitation
            # new user will use it at /register page
            # and new user will be created or attached to existed user after it
            # hash store in DB together with:
            # - reqid
            # - create date/time 
            # - VNT
            # - nickname
            # - group 
            # - hash as checksum for user email
            # email checksum hash is to allow user register only with specific email if needed by request creator
            reqhash = db.new_reg_request_hash(vntid, groupname, nickname, source_uservntid)
            # now we have user in registration queue
            # now we need to send reply with reqhash
            #dst_uservntid = 
            # Response message
            vntname = db.db_vnt_get(vntid).vntname
            data = {
                #'reqid': request['reqid'],
                #'action': 'Response',
                'dst_uservntid': request['src_uservntid'],
                #'which_dst': 1,
                'operation': 'Done',
                'cur_uservntid': cur_uservntid,
                'src_uservntid': source_uservntid,
                'formbody_json': [
                    {'name': 'code', 'value': reqhash },
                    {'name': 'vntname', 'value': vntname },
                    {'name': 'nickname', 'value': nickname }
                    #{'name': 'email', 'value': email }
                ]
            }
            message = 'User '+nickname+' for vnt '+vntname+' with group '+groupname+' is ready for registration'
            #db.db_change_message_direction_to_backward(reqid, cur_uservntid)
            #db.db_request_response(reqid, data)
            #db.db_route_request2(reqid, token, url)
        # ====== Change User Group ======
        # changeusergroup
        if request['operation'] == 'changeusergroup':
            nickname = ''
            uvntid = None
            old_groupname = ''
            old_groupid = None
            new_groupname = ''
            new_groupid = None
            #message = ''
            operation = ''
            for i in request['formbody_json']:
                if i['name'] == 'user old nickname':
                    nickname = i['value']
                if i['name'] == 'user old uservntid':
                    uvntid = i['value']
                if i['name'] == 'user old groupname':
                    old_groupname = i['value']
                if i['name'] == 'user old groupid':
                    old_groupid = i['value']
                if i['name'] == 'user new groupname':
                    new_groupname = i['value']
                if i['name'] == 'user new groupid':
                    new_groupid = i['value']
            # try to check that network connectivity will not be broken on user remove
            if pcalc.check_connectivity(vntid, uvntid):
                operation = 'Done'
                message = 'User '+nickname+' moved from group '+old_groupname+' to group '+new_groupname
                if new_groupid and uvntid:
                    try:
                        grpusrid = db.db_grpusr_new(new_groupid, uvntid)
                        db.db_grpusr_del(old_groupid, uvntid)
                    except:
                        operation = 'Failed'
                        message = 'User '+nickname+' cant be moved from group '+old_groupname+' to group '+new_groupname
                    if not grpusrid:
                        operation = 'Failed'
                        message = 'User '+nickname+' cant be moved from group '+old_groupname+' to group '+new_groupname
                else:
                    operation = 'Failed'
                    message = 'User '+nickname+' cant be moved from group '+old_groupname+' to group '+new_groupname
            else:
                operation = 'Error'
                message = 'User '+nickname+' cant be moved from group '+old_groupname+' to group '+new_groupname+' as it will break VNT connectivity'
            data = {
                #'reqid': request['reqid'],
                #'action': 'Response',
                'dst_uservntid': request['src_uservntid'],
                #'which_dst': 1,
                'operation': operation,
                'cur_uservntid': cur_uservntid,
                'src_uservntid': source_uservntid,
                'formbody_json': [
                    {'name': 'nickname', 'value': nickname },
                    {'name': 'old group', 'value': old_groupname},
                    {'name': 'new group', 'value': new_groupname},
                    {'name': 'message', 'value': message}
                ]
            }
        # ====== Del User From Group ======   
        if request['operation'] == 'deluserfromgroup':
            old_nickname = ''
            old_uservntid = None
            groupname = ''
            groupid = None
            message = ''
            operation = ''
            for i in request['formbody_json']:
                if i['name'] == 'user old nickname':
                    old_nickname = i['value']
                if i['name'] == 'user old uservntid':
                    old_uservntid = i['value']
                if i['name'] == 'groupname':
                    groupname = i['value']
                if i['name'] == 'groupid':
                    groupid = i['value']
            # try to check that network connectivity will not be broken on user remove
            if pcalc.check_connectivity(vntid, old_uservntid):
                operation = 'Done'
                message = 'User '+old_nickname+' removed from group '+groupname
                if groupid and old_uservntid:
                    try:
                        db.db_grpusr_del(groupid, old_uservntid)
                    except:
                        operation = 'Failed'
                        message = 'User '+old_nickname+' cant be removed from group '+groupname
                else:
                    operation = 'Failed'
                    message = 'User '+old_nickname+' cant be removed from group '+groupname
            else:
                operation = 'Error'
                message = 'User '+old_nickname+' cant be removed from group '+groupname+' as it will break VNT connectivity'
            data = {
                #'reqid': request['reqid'],
                #'action': 'Response',
                'dst_uservntid': request['src_uservntid'],
                #'which_dst': 1,
                'operation': operation,
                'cur_uservntid': cur_uservntid,
                'src_uservntid': source_uservntid,
                'formbody_json': [
                    {'name': 'nickname', 'value': old_nickname },
                    {'name': 'old group', 'value': groupname},
                    {'name': 'message', 'value': message}
                ]
            }
        # ====== Add User To Group ======
        # addusertogroup
        if request['operation'] == 'addusertogroup':
            nickname = ''
            groupname = ''
            for i in request['formbody_json']:
                if i['name'] == 'user old nickname':
                    nickname = i['value']
                if i['name'] == 'groupname':
                    groupname = i['value']
            operation = 'Done'
            grpusrid = None
            if nickname and groupname:
                groupid = db.db_get_group_id_from_name(groupname)
                uservntid = db.db_uservntid_from_usernick(nickname)
                if groupid and uservntid:
                    try:
                        grpusrid = db.db_grpusr_new(groupid, uservntid)
                    except:
                        operation = 'Failed'
                    if not grpusrid:
                        operation = 'Failed'
                else:
                    operation = 'Failed'
            else:
                operation = 'Failed'
            data = {
                #'reqid': request['reqid'],
                #'action': 'Response',
                'dst_uservntid': request['src_uservntid'],
                #'which_dst': 1,
                'operation': operation,
                'cur_uservntid': cur_uservntid,
                'src_uservntid': source_uservntid,
                'formbody_json': [
                    {'name': 'nickname', 'value': nickname },
                    {'name': 'groupname', 'value': groupname }
                ]
            }
            message = 'Users Bot', 'User '+nickname+' added to group '+groupname
        # ====== Change User Nickname ======
        # changenickname
        if request['operation'] == 'changenickname':
            newnickname = ''
            oldnickname = ''
            olduservntid = None
            for i in request['formbody_json']:
                if i['name'] == 'user nickname':
                    nickname = i['value']
                if i['name'] == 'user old nickname':
                    oldnickname = i['value']
                if i['name'] == 'user old uservntid':
                    olduservntid = i['value']
            operation = 'Done'
            message = ''
            if nickname and oldnickname and olduservntid:
                message = 'User '+oldnickname+' changed to '+nickname
                try:
                    db.db_uservnt_change_nickname(olduservntid, nickname)
                except:
                    operation = 'Error'
                    message = 'User '+oldnickname+' was not changed to '+nickname+': database error'
            else:
                operation = 'Failed'
                message = 'User '+oldnickname+' was not changed to '+nickname+': not correct input'
            data = {
                #'reqid': request['reqid'],
                #'action': 'Response',
                'dst_uservntid': request['src_uservntid'],
                #'which_dst': 1,
                'operation': operation,
                'cur_uservntid': cur_uservntid,
                'src_uservntid': source_uservntid,
                'formbody_json': [
                    {'name': 'New Nickname', 'value': nickname },
                    {'name': 'Old Nickname', 'value': oldnickname }
                ]
            }
        # ====== Add User To Service ======
        # addtoservice
        if request['operation'] == 'addtoservice':
            old_nickname = ''
            old_uservntid = None
            new_sname = ''
            new_sid = None
            for i in request['formbody_json']:
                if i['name'] == 'user old nickname':
                    old_nickname = i['value']
                if i['name'] == 'user old uservntid':
                    old_uservntid = i['value']
                if i['name'] == 'serviceid':
                    new_sid = i['value']
                if i['name'] == 'service name':
                    new_sname = i['value']
            #{'name': 'user old nickname', 'value': vntbot.manageform.user[0] },
            #{'name': 'user old uservntid', 'value': vntbot.manageform.user[1] },
            #{'name': 'serviceid', 'value': vntbot.manageform.serviceid[0] },
            #{'name': 'service name', 'value': vntbot.manageform.serviceid[1] },
            operation = 'Done'
            message = ''
            if old_nickname and old_uservntid and new_sname and new_sid:
                message = 'User '+nickname+' added to Service '+new_sname
                try:
                    db.db_svcusr_new(vntid, new_sid, old_uservntid)
                except:
                    operation = 'Error'
                    message = 'User '+nickname+' was not added to Service '+new_sname+': database error'
            else:
                operation = 'Failed'
                message = 'User '+nickname+' was not added to Service '+new_sname+': incorrect input'
            data = {
                #'reqid': request['reqid'],
                #'action': 'Response',
                'dst_uservntid': request['src_uservntid'],
                #'which_dst': 1,
                'operation': operation,
                'cur_uservntid': cur_uservntid,
                'src_uservntid': source_uservntid,
                'formbody_json': [
                    {'name': 'nickname', 'value': old_nickname },
                    {'name': 'Service Name', 'value': new_sname }
                ]
            }
        # ====== Remove User From Service ======
        # removefromservice
        if request['operation'] == 'removefromservice':
            old_nickname = ''
            old_uservntid = None
            new_sname = ''
            new_sid = None
            for i in request['formbody_json']:
                if i['name'] == 'user old nickname':
                    old_nickname = i['value']
                if i['name'] == 'user old uservntid':
                    old_uservntid = i['value']
                if i['name'] == 'serviceid':
                    new_sid = i['value']
                if i['name'] == 'service name':
                    new_sname = i['value']
            #{'name': 'user old nickname', 'value': vntbot.manageform.user[0] },
            #{'name': 'user old uservntid', 'value': vntbot.manageform.user[1] },
            #{'name': 'serviceid', 'value': vntbot.manageform.serviceid[0] },
            #{'name': 'service name', 'value': vntbot.manageform.serviceid[1] },
            operation = 'Done'
            message = ''
            if old_nickname and old_uservntid and new_sname and new_sid:
                message = 'User '+nickname+' removed from Service '+new_sname
                try:
                    db.db_usr_del_service(vntid, old_uservntid, new_sid)
                except:
                    operation = 'Error'
                    message = 'User '+nickname+' was not removed from Service '+new_sname+': database error'
            else:
                operation = 'Failed'
                message = 'User '+nickname+' was not removed from Service '+new_sname+': incorrect input'
            data = {
                #'reqid': request['reqid'],
                #'action': 'Response',
                'dst_uservntid': request['src_uservntid'],
                #'which_dst': 1,
                'operation': operation,
                'cur_uservntid': cur_uservntid,
                'src_uservntid': source_uservntid,
                'formbody_json': [
                    {'name': 'nickname', 'value': old_nickname },
                    {'name': 'Service Name', 'value': new_sname }
                ]
            }
        # ====== Delete User ======
        # deleteuser
        if request['operation'] == 'deleteuser':
            old_nickname = ''
            old_uservntid  = None
            for i in request['formbody_json']:
                if i['name'] == 'user old nickname':
                    old_nickname = i['value']
                if i['name'] == 'user old uservntid':
                    old_uservntid = i['value']
            # {'name': 'user old nickname', 'value': vntbot.manageform.user[0] },
            # {'name': 'user old uservntid', 'value': vntbot.manageform.user[1] },
            operation = 'Done'
            message = ''
            if old_nickname and old_uservntid:
                message = 'User '+old_nickname+' removed from VNT'
                if pcalc.check_connectivity(vntid, old_uservntid):
                    try:
                        # delete all services from this user
                        db.db_svcusr_del(old_uservntid)
                        # delete this user from all groups
                        db.db_grpusr_del_uservntid(old_uservntid)
                        # delete uservntid
                        db.db_uservnt_delete_one(vntid, old_uservntid)
                        db.db_commit()
                    except:
                        operation = 'Error'
                        message = 'User '+nickname+' was not removed from VNT: database error'
                else:
                    operation = 'Failed'
                    message = 'User '+nickname+' impossible to remove from VNT without connection break, create redundand connection first'
            else:
                operation = 'Failed'
                message = 'User '+nickname+' was not removed from VNT: incorrect input'
            data = {
                #'reqid': request['reqid'],
                #'action': 'Response',
                'dst_uservntid': request['src_uservntid'],
                #'which_dst': 1,
                'operation': operation,
                'cur_uservntid': cur_uservntid,
                'src_uservntid': source_uservntid,
                'formbody_json': [
                    {'name': 'old nickname', 'value': old_nickname },
                    {'name': 'old uservntid', 'value': old_uservntid }
                ]
            }
        # ====== Destroy User ======
        if request['operation'] == 'destroyuser':
            old_nickname = ''
            old_uservntid  = 0
            message = ''
            for i in request['formbody_json']:
                if i['name'] == 'user old nickname':
                    old_nickname = i['value']
                if i['name'] == 'user old uservntid':
                    old_uservntid = i['value']
            print("old_uservntid=", old_uservntid)
            # find userid from uservntid
            old_userid = db.db_uservntid_entry(old_uservntid).userid
            print("old_userid=", old_userid)
            # check connectivity
            if pcalc.check_connectivity_for_userid(old_userid):
                # delete all services from this user
                db.db_svcusr_del_for_userid(old_userid)
                # delete this user from all groups
                db.db_grpusr_del_user(old_userid) # delete user from all groups
                # delete uservntid
                db.db_uservnt_delete_all(old_userid)
                # delete userid
                db.userauthObj.db_del_userid(old_userid)
                message = 'User '+old_nickname+' destroyed'
            else:
                message = 'User '+old_nickname+' cant be destroyed as it will break VNT connectivity'
            data = {
                #'reqid': request['reqid'],
                #'action': 'Response',
                'dst_uservntid': request['src_uservntid'],
                #'which_dst': 1,
                'operation': 'Done',
                'cur_uservntid': cur_uservntid,
                'src_uservntid': source_uservntid,
                'formbody_json': [
                    {'name': 'old nickname', 'value': old_nickname },
                    {'name': 'old uservntid', 'value': old_uservntid }
                ]
            }
        # send message back
        db.db_add_reqchange(cur_uservntid, reqid, 'Users Bot', message)
        db.db_request_response(reqid, data, cur_uservntid)
        db.db_route_request2(reqid, token, url)
        return

