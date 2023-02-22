from server import db

class bot:
    def __init__(self):
        self.name = 'Services management'
        return
    def run_bot(self, request, vntid, token, url):
        #print("services management bot is running")
        # we have parsed request message in 'request'
        #print("message for process=", request)
        """
        message for process= {
            'reqid': 3,
            'cur_uservntid': 4,
            'cur_name': 'services',
            'src_uservntid': 1,
            'src_name': 'rom',
            'which_dst': 2,
            'dst_uservntid': None,
            'dst_name': '',
            'dst_presvcid': None,
            'dst_presvc_name': '',
            'dst_svcid': 3,
            'dst_svc_name': 'admin.services',
            'subject': 'test request for new service bill.sign',
            'comment': 'descr test request for new service bill.sign',
            'created': datetime.datetime(2020, 6, 18, 7, 54, 20),
            'changed': datetime.datetime(2020, 6, 18, 7, 54, 21),
            'action': 'Requested',
            'operation': 'add',
            'storage': '',
            'formid': 0,
            'formbody_json': [
                {'name': 'servicecode1', 'value': 'bill'}, 
                {'name': 'servicecode2', 'value': 'sign'},
                {'name': 'description', 'value': 'test service'},
                { 'name': 'nickname', 'value': 'testuser2' }
            ]
        }
        """
        cur_uservntid = request['cur_uservntid']
        source_uservntid = request['src_uservntid']
        reqid = request['reqid']
        data = {}
        if request['operation'] == 'add':
            preservices = None
            scode1 = None
            scode2 = None
            scode3 = None
            scode4 = None
            description = ''
            nickname = ''
            actions = []
            variables = []
            storage = False
            for i in request['formbody_json']:
                if i['name'] == 'servicecode1':
                    scode1 = i['value']
                if i['name'] == 'servicecode2':
                    scode2 = i['value']
                if i['name'] == 'servicecode3':
                    scode3 = i['value']
                if i['name'] == 'servicecode4':
                    scode4 = i['value']
                if i['name'] == 'nickname':
                    nickname = i['value']
                if i['name'] == 'description':
                    description = i['value']
                if i['name'] == 'actions':
                    actions = i['value']
                if i['name'] == 'variables':
                    variables = i['value']
                if i['name'] == 'preservices':
                    preservices = i['value']
                if i['name'] == 'storage':
                    if i['value'] == 'true':
                        storage = True
            # add new service
            #print("actions=", actions)
            #print("variables=", variables)
            #svc_formid = db.db_form_new('', description, actions, variables)
            svc_svcid = db.db_svc_new(vntid, description, scode1, scode2, scode3, scode4, '', actions, variables)
            uservntid = db.db_uservntid_from_usernick(nickname)
            db.db_svcusr_new(vntid, svc_svcid, uservntid) # add service to nickname
            # add pre-services if any
            if preservices:
                for p in preservices:
                    print("******** preservice to add:", p)
                    db.db_add_presvcitem_for_svc(svc_svcid, p['presvcid'], p['ordernum'])
            data = {
                'dst_uservntid': source_uservntid,
                'operation': 'Done',
                'cur_uservntid': cur_uservntid,
                'src_uservntid': cur_uservntid,
                'formbody_json': [
                    {'name': 'nickname', 'value': nickname },
                    {'name': 'description', 'value': description}
                ]
            }
            db.db_add_reqchange(cur_uservntid, reqid, 'Services Bot', 'Service '+description+' created and assigned to '+nickname)
        if request['operation'] == 'del':
            serviceid = None
            for i in request['formbody_json']:
                if i['name'] == 'serviceid':
                    serviceid = i['value']
            if serviceid:
                # delete service links to all users
                db.db_svcusr_del_for_service(serviceid)
                # delete service
                db.db_svc_del(serviceid)
            # generate reply Done
            data = {
                'dst_uservntid': source_uservntid,
                'operation': 'Done',
                'cur_uservntid': cur_uservntid,
                'src_uservntid': cur_uservntid,
                'formbody_json': [
                    {'name': 'servicecode', 'value': serviceid }
                ]
            }
            db.db_add_reqchange(cur_uservntid, reqid, 'Services Bot', 'Service '+str(serviceid)+' deleted')
        #db.db_change_message_direction_to_backward(reqid, cur_uservntid)
        db.db_request_response(reqid, data, cur_uservntid)
        db.db_route_request2(reqid, token, url)
        return
