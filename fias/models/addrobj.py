#coding: utf-8
from __future__ import unicode_literals, absolute_import

import six

from django.conf import settings
from django.db import models

from fias.config import FIAS_DATABASE_ALIAS
from fias.fields import UUIDField
from fias.models.common import Common

__all__ = ['AddrObj']


class AddrObj(Common):

    class Meta:
        app_label = 'fias'
        index_together = (
            ('aolevel', 'shortname'),
            ('shortname', 'formalname'),
        )
        ordering = ['aolevel', 'formalname']

    aoguid = UUIDField(primary_key=True)
    parentguid = UUIDField(blank=True, null=True, db_index=True)
    aoid = UUIDField(db_index=True, unique=True)
    previd = UUIDField(blank=True, null=True)
    nextid = UUIDField(blank=True, null=True)

    formalname = models.CharField(max_length=120, db_index=True)
    offname = models.CharField(max_length=120, blank=True, null=True)
    shortname = models.CharField(max_length=10, db_index=True)
    aolevel = models.PositiveSmallIntegerField(db_index=True)

    #KLADE
    regioncode = models.CharField(max_length=2)
    autocode = models.CharField(max_length=1)
    areacode = models.CharField(max_length=3)
    citycode = models.CharField(max_length=3)
    ctarcode = models.CharField(max_length=3)
    placecode = models.CharField(max_length=3)
    streetcode = models.CharField(max_length=4)
    extrcode = models.CharField(max_length=4)
    sextcode = models.CharField(max_length=3)

    #KLADR
    code = models.CharField(max_length=17, blank=True, null=True)
    plaincode = models.CharField(max_length=15, blank=True, null=True)

    actstatus = models.BooleanField()
    centstatus = models.PositiveSmallIntegerField()
    operstatus = models.PositiveSmallIntegerField()
    currstatus = models.PositiveSmallIntegerField()

    livestatus = models.BooleanField()

    def full_name(self, depth=None, formal=False):
        assert isinstance(depth, six.integer_types), 'Depth must be integer'

        if not self.parentguid or self.aolevel <= 1 or depth <= 0:
            if formal:
               return self.get_formal_name()
            return self.get_natural_name()
        else:
            parent = AddrObj.objects.get(pk=self.parentguid)
            return '{}, {}'.format(parent.full_name(depth-1, formal), self)

    def get_natural_name(self):
        if self.aolevel == 1:
            return '{} {}'.format(self.formalname, self.shortname)
        return self.get_formal_name()

    def get_formal_name(self):
        return '{} {}'.format(self.shortname, self.formalname)

    def __unicode__(self):
        return self.get_natural_name()

    @property
    def full_address(self):
        return self.full_name(5)

    def get_city(self, formal=False):
        if not self.parentguid or self.aolevel <= 1:
            return None
        parent = self
        aolevel = self.aolevel
        if aolevel == 4:
            return self.get_formal_name()            
        while aolevel >= 5:
            parent = AddrObj.objects.get(pk=parent.parentguid)
            aolevel = parent.aolevel
            if aolevel == 4:
                return parent.get_formal_name()            
        return None

    @property
    def sphinx(self):
        from fias.sphinxit import search
        query = search().match('@aoguid "%s"' % self.aoguid, raw=True)
        result = query.ask()
        print result
        items = result['result']['items']
        print "!!!!!!!!!!!!!fdfd"
        print items

        return items

        
if 'mysql' in settings.DATABASES[FIAS_DATABASE_ALIAS]['ENGINE']:
    from fias.models.sphinx import AddrObjIndex
    __all__ = ['AddrObj', 'AddrObjIndex']
