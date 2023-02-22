#import os
#import requests
from server import db

class bot:
    def __init__(self):
        self.name = 'Groups management'
        return
    def run_bot(self, request, vntid, token, url):
        #print("groups management bot is running")
        #
        #print("message for process=", request)
        cur_uservntid = request['cur_uservntid']
        source_uservntid = request['src_uservntid']
        reqid = request['reqid']
        data = {}
        if request['operation'] == 'add':
            """ create new group """
            #print("* create new group")
            """
                'formbody_json': [
                    {'name': 'groupname', 'value': 'test2'}, 
                    {'name': 'group description', 'value': 'test2 group'}, 
                    {'name': 'gw user nickname', 'value': 'rom'}
                ]
            """
            gw_user_name = ''
            description = ''
            group_name = ''
            for i in request['formbody_json']:
                if i['name'] == 'groupname':
                    group_name = i['value']
                if i['name'] == 'group description':
                    description = i['value']
                if i['name'] == 'gw user nickname':
                    gw_user_name = i['value']
            fbody = request['formbody_json']
            uservntid = request['src_uservntid']
            payload = {
                'uservntid': uservntid,
                'vntid': vntid,
                'gw_user_name': gw_user_name,
                'description': description,
                'groupname': group_name
            }
            # create group, get groupid           
            groupid = db.db_group_new(vntid, group_name, description)
            # get uservntid from known nickname
            gw_uservntid = db.db_uservntid_from_usernick(gw_user_name)
            # attach this user as gateway and new user to the new group
            db.db_grpusr_new(groupid, gw_uservntid)
            # for external bots it can be used API call:
            #ret = requests.post(url+'/api/bot/newgroup', headers={'Authorization': 'JWT '+token}, data=payload)
            #print("bot req out=", ret.json())
            # and we need to make log message to change message status
            # ***
            # plus we need to create reply message back to source uservntid with status "Done"
            # ***
            data = {
                'dst_uservntid': source_uservntid,
                'operation': 'Done',
                'cur_uservntid': cur_uservntid,
                'src_uservntid': cur_uservntid,
                'formbody_json': [
                    {'name': 'groupname', 'value': group_name }
                ]
            }
            db.db_add_reqchange(cur_uservntid, reqid, 'Bots Bot', 'Group '+group_name+' created with first user '+gw_user_name)
        if request['operation'] == 'del':
            groupid_del = None
            for i in request['formbody_json']:
                if i['name'] == 'groupidfordel':
                    groupid_del = i['value']
            if groupid_del:
                # just delete? what if we will have disconnected users there?
                # ToDo: find solution - check all the group users that they are in other groups too
                # plus we need to remove all the users from this group before delete
                # right now if I delete group with below code, I have dijkstra routing problem when calculate available
                # services for user, need to add checks about groups/users/services paths consystensy
                db.db_grpusr_del_all(groupid_del)   # delete all users from group
                db.db_group_delete(groupid_del)     # delete group from VNT
            data = {
                'dst_uservntid': source_uservntid,
                'operation': 'Done',
                'cur_uservntid': cur_uservntid,
                'src_uservntid': cur_uservntid,
                'formbody_json': [
                    {'name': 'groupid', 'value': groupid_del }
                ]
            }
            db.db_add_reqchange(cur_uservntid, reqid, 'Groups Bot', 'Group '+str(groupid_del)+' deleted')
        #db.db_change_message_direction_to_backward(reqid, cur_uservntid)
        db.db_request_response(reqid, data, cur_uservntid)
        db.db_route_request2(reqid, token, url)
        return
