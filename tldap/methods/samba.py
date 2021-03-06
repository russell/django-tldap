# Copyright 2012-2014 VPAC
#
# This file is part of django-tldap.
#
# django-tldap is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# django-tldap is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with django-tldap  If not, see <http://www.gnu.org/licenses/>.

""" Methods specific to Samba attributes. Not applicable for Samba 4 AD
support. """

import smbpasswd
import datetime

class sambaAccountMixin(object):
    @classmethod
    def __unicode__(cls, self):
        return u"%s"%(self.displayName or self.cn)

    @classmethod
    def setup_from_master(cls, self, master):
        self.sambaSID = getattr(master, "objectSid", None) or getattr(master, "sambaSID", None)

    @classmethod
    def pre_add(cls, self):
        settings = self._settings
        if self.sambaAcctFlags is None:
            self.sambaAcctFlags = '[ U         ]'
        if self.sambaPwdLastSet is None:
            self.sambaPwdLastSet = datetime.datetime.now()
        if self.sambaSID is None:
            rid_base = settings['SAMBA_ACCOUNT_RID_BASE']
            assert rid_base % 2 == 0
            self.sambaSID = "S-1-5-" + settings['SAMBA_DOMAIN_SID'] + "-" + str(int(self.uidNumber)*2 + rid_base)
        if self.sambaDomainName is None:
            self.sambaDomainName = settings['SAMBA_DOMAIN_NAME']

    @classmethod
    def lock(cls, self):
        self.sambaAcctFlags = '[DU         ]'

    @classmethod
    def unlock(cls, self):
        self.sambaAcctFlags = '[ U         ]'

    @classmethod
    def change_password(cls, self, password):
        if isinstance(password, unicode):
            password = password.encode()
        self.sambaNTPassword=smbpasswd.nthash(password)
        self.sambaLMPassword=smbpasswd.lmhash(password)
        self.sambaPwdMustChange=None
        self.sambaPwdLastSet=datetime.datetime.now()


class sambaGroupMixin(object):
    @classmethod
    def __unicode__(cls, self):
        return u"%s"%(self.displayName or self.cn)

    @classmethod
    def setup_from_master(cls, self, master):
        self.sambaSID = getattr(master, "objectSid", None) or getattr(master, "sambaSID", None)

    @classmethod
    def pre_add(cls, self):
        settings = self._settings
        if self.sambaGroupType is None:
            self.sambaGroupType = 2
        if self.sambaSID is None:
            rid_base = settings['SAMBA_GROUP_RID_BASE']
            assert rid_base % 2 == 0
            self.sambaSID = "S-1-5-" + settings['SAMBA_DOMAIN_SID'] + "-" + str(int(self.gidNumber)*2 + 1 + rid_base)

    @classmethod
    def pre_save(cls, self):
        if self.displayName is None:
            self.displayName = self.cn
