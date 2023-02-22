from server import db

class bot:
    def __init__(self):
        self.name = 'Bots management'
        return
    def run_bot(self, request, vntid, token, url):
        #print("bots management bot is running")
        #print("message for process=", request)
        """
            message for process= {
                'reqid': 1,
                'cur_uservntid': 2,
                'cur_name': 'bots',
                'src_uservntid': 1,
                'src_name': 'rom',
                'which_dst': 2,
                'dst_uservntid': None,
                'dst_name': '', 
                'dst_presvcid': None,
                'dst_presvc_name': '',
                'dst_svcid': 1,
                'dst_svc_name':
                'admin.bots',
                'subject': 'test request for add bot null to user testbot group test2',
                'comment': 'descr test request for add bot null to user testbot in group test2', 
                'created': datetime.datetime(2020, 6, 18, 1, 33, 59),
                'changed': datetime.datetime(2020, 6, 18, 1, 34),
                'action': 'Requested', 
                'operation': 'add', 
                'storage': '', 
                'formid': 0,
                'formbody_json': [
                    {'name': 'nickname', 'value': 'testuser2'}, {'name': 'fromallbots', 'value': 5},
                    {'name': 'botidfordel', 'value': 0}, {'name': 'groupid', 'value': 0}
                ]
            }
        """
        cur_uservntid = request['cur_uservntid']
        source_uservntid = request['src_uservntid']
        reqid = request['reqid']
        data = {}
        # collect needed information
        bot_id = None
        bot_id_del = None
        nickname = ''
        group_id = None
        for i in request['formbody_json']:
            if i['name'] == 'nickname':
                nickname = i['value']
            if i['name'] == 'fromallbots':
                bot_id = i['value']
            if i['name'] == 'botidfordel':
                bot_id_del = i['value']
            if i['name'] == 'groupid':
                group_id = i['value']
        if request['operation'] == 'add':
            # add new bot
            bot_vntid = db.db_botvnt_new(bot_id, vntid, nickname) # create user for bot in vnt
            db.db_grpusr_new(group_id, bot_vntid) # add bot to group 'adm'
            data = {
                'dst_uservntid': source_uservntid,
                'operation': 'Done',
                'cur_uservntid': cur_uservntid,
                'src_uservntid': cur_uservntid,
                'formbody_json': [
                    { 'name': 'nickname', 'value': nickname },
                    { 'name': 'fromallbots', 'value': bot_id },
                    { 'name': 'botidfordel', 'value': bot_id_del },
                    { 'name': 'groupid', 'value': group_id }
                ]
            }
            db.db_add_reqchange(cur_uservntid, reqid, 'Bots Bot', 'Bot added to group and assigned to user '+nickname)
            #print("bot and user created=", nickname)
        if request['operation'] == 'del':
            # del bot user from group
            db.db_grpusr_del(group_id, bot_id_del)
            # del service from user entry
            db.db_svcusr_del(bot_id_del)
            # del user entry for bot
            print("*** try to del ", bot_id_del)
            db.db_botvnt_del(bot_id_del, vntid)
            data = {
                'dst_uservntid': source_uservntid,
                'operation': 'Done',
                'cur_uservntid': cur_uservntid,
                'src_uservntid': cur_uservntid,
                'formbody_json': [
                    { 'name': 'nickname', 'value': nickname }
                ]
            }
            db.db_add_reqchange(cur_uservntid, reqid, 'Bots Bot', 'Bot deleted from user '+nickname)
        #db.db_change_message_direction_to_backward(reqid, cur_uservntid)
        db.db_request_response(reqid, data, cur_uservntid)
        db.db_route_request2(reqid, token, url)
        return
