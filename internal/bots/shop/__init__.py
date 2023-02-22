# botshop bot
from server import db


class bot:
    def __init__(self):
        self.name = "BotShop Management"
        return
    def run_bot(self, request, vntid, token, url):
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
        source_uservntid = request["src_uservntid"]
        cur_uservntid = request["cur_uservntid"]
        reqid = request["reqid"]
        data = {}
        nickname = ""
        if request["operation"] == "createnewuser":
            nickname = ""
            groupname = ""
            email = None
            for i in request["formbody_json"]:
                if i["name"] == "user nickname":
                    nickname = i["value"]
                if i["name"] == "groupname":
                    groupname = i['value']
                if i['name'] == 'email':
                    if i['value']:
                        email = i['value']
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
            reqhash = db.new_reg_request_hash(vntid, groupname, nickname, email, source_uservntid)
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
                    {'name': 'nickname', 'value': nickname },
                    {'name': 'email', 'value': email }
                ]
            }
            db.db_add_reqchange(cur_uservntid, reqid, 'Users Bot', 'User '+nickname+' added to group '+groupname)
            #db.db_change_message_direction_to_backward(reqid, cur_uservntid)
            #db.db_request_response(reqid, data)
            #db.db_route_request2(reqid, token, url)
        # changeusergroup
        if request['operation'] == 'changeusergroup':
            data = {
                #'reqid': request['reqid'],
                #'action': 'Response',
                'dst_uservntid': request['src_uservntid'],
                #'which_dst': 1,
                'operation': 'Done',
                'cur_uservntid': cur_uservntid,
                'src_uservntid': source_uservntid,
                'formbody_json': [
                    {'name': 'nickname', 'value': nickname },
                ]
            }
            db.db_add_reqchange(cur_uservntid, reqid, 'Users Bot', 'User '+nickname+' moved to group '+groupname)
        # addusertogroup
        if request['operation'] == 'addusertogroup':
            data = {
                #'reqid': request['reqid'],
                #'action': 'Response',
                'dst_uservntid': request['src_uservntid'],
                #'which_dst': 1,
                'operation': 'Done',
                'cur_uservntid': cur_uservntid,
                'src_uservntid': source_uservntid,
                'formbody_json': [
                    {'name': 'nickname', 'value': nickname },
                ]
            }
            db.db_add_reqchange(cur_uservntid, reqid, 'Users Bot', 'User '+nickname+' added to group '+groupname)
        # changenickname
        if request['operation'] == 'changenickname':
            data = {
                #'reqid': request['reqid'],
                #'action': 'Response',
                'dst_uservntid': request['src_uservntid'],
                #'which_dst': 1,
                'operation': 'Done',
                'cur_uservntid': cur_uservntid,
                'src_uservntid': source_uservntid,
                'formbody_json': [
                    {'name': 'nickname', 'value': nickname },
                ]
            }
            db.db_add_reqchange(cur_uservntid, reqid, 'Users Bot', 'User '+nickname+' changed ')
        # addtoservice
        if request['operation'] == 'addtoservice':
            data = {
                #'reqid': request['reqid'],
                #'action': 'Response',
                'dst_uservntid': request['src_uservntid'],
                #'which_dst': 1,
                'operation': 'Done',
                'cur_uservntid': cur_uservntid,
                'src_uservntid': source_uservntid,
                'formbody_json': [
                    {'name': 'nickname', 'value': nickname },
                ]
            }
            db.db_add_reqchange(cur_uservntid, reqid, 'Users Bot', 'User '+nickname+' added to gservice ')
        # removefromservice
        if request['operation'] == 'removefromservice':
            data = {
                #'reqid': request['reqid'],
                #'action': 'Response',
                'dst_uservntid': request['src_uservntid'],
                #'which_dst': 1,
                'operation': 'Done',
                'cur_uservntid': cur_uservntid,
                'src_uservntid': source_uservntid,
                'formbody_json': [
                    {'name': 'nickname', 'value': nickname },
                ]
            }
            db.db_add_reqchange(cur_uservntid, reqid, 'Users Bot', 'User '+nickname+' removed from gservice ')
        # deleteuser
        if request['operation'] == 'deleteuser':
            data = {
                #'reqid': request['reqid'],
                #'action': 'Response',
                'dst_uservntid': request['src_uservntid'],
                #'which_dst': 1,
                'operation': 'Done',
                'cur_uservntid': cur_uservntid,
                'src_uservntid': source_uservntid,
                'formbody_json': [
                    {'name': 'nickname', 'value': nickname },
                ]
            }
            db.db_add_reqchange(cur_uservntid, reqid, 'Users Bot', 'User '+nickname+' deleted')
        #db.db_change_message_direction_to_backward(reqid, cur_uservntid)
        db.db_request_response(reqid, data, cur_uservntid)
        db.db_route_request2(reqid, token, url)
        return

