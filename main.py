#!/usr/bin/python2

import xml.etree.ElementTree as ET
import requests


def get_auth_token(plex_user, plex_pass):
    auth_url = 'https://my.plexapp.com/users/sign_in.xml'
    auth_params = {'user[login]': plex_user,
                   'user[password]': plex_pass
                   }

    headers = {
        'X-Plex-Product': 'Plex API',
        'X-Plex-Version': "0.2",
        'X-Plex-Client-Identifier': '112286'
    }

    try:
        auth_request = requests.post(auth_url, headers=headers, data=auth_params)
        auth_response = auth_request.content
        root = ET.fromstring(auth_response)
        try:
            plex_auth_token = root.attrib['authToken']
            return plex_auth_token
        except KeyError:
            print 'ERROR: Plex Username/Password Incorrect. Try again.'
            return None
    except requests.Timeout or requests.ConnectionError or requests.HTTPError:
        return None


def get_session_data(plex_url, plex_port, plex_token):

    plex_url = 'http://{}:{}/status/sessions'.format(plex_url, plex_port)

    plex_params = {
        'X-Plex-Token': plex_token
    }

    plex_response = requests.get(plex_url, params=plex_params)
    plex_content = plex_response.content
    return plex_content


def parse_session_data(xmlfile):
    display_string, user_name, player_platform, player_state = '', '', '', ''
    display_list = []
    root = ET.fromstring(xmlfile)

    num_videos = root.get('size')
    if int(num_videos) > 0:
        display_list.append('PLEX API: There is/are {} video(s) playing'.format(num_videos))
    else:
        display_list.append('PLEX API: There are currently no videos playing')
    for video in root.findall('Video'):
        if video.get('type') == 'episode':
            show_title = video.get('grandparentTitle')
            episode_title = video.get('title')
            display_string = '%s: %s' % (show_title, episode_title)
        elif video.get('type') == 'movie':
            movie_title = video.get('title')
            movie_year = video.get('year')
            display_string = '%s (%s)' % (movie_title, movie_year)
        for user in video.findall('User'):
            user_name = user.get('title')
        for player in video.findall('Player'):
            player_platform = player.get('platform')
            player_state = player.get('state')

        display_list.append('{} is watching {} on {} ({})'.format(user_name, display_string, player_platform, player_state))

    return display_list


if __name__ == '__main__':
    #EXAMPLE
    plex_token = get_auth_token('username', 'password')
    if plex_token is not None:
        plex_content = get_session_data('192.168.1.x', '32400', plex_token)
        for display_string in parse_session_data(plex_content):
            print display_string

