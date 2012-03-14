import unittest2 as unittest

from zope.component import testing
from zope.component import provideSubscriptionAdapter
from zope.component import provideAdapter

from collective.jekyll.interfaces import ISymptomFactory
from collective.jekyll.interfaces import IDiagnosis
from collective.jekyll.symptoms import SymptomFactory
from collective.jekyll.symptoms import Symptom
from collective.jekyll.diagnosis import Diagnosis


class Counter(object):

    def __init__(self):
        self.clear()

    def clear(self):
        self.value = 0

    def inc(self):
        self.value += 1

    def __str__(self):
        return repr(self.value)

counter = Counter()


def getValues(seq):
    return [value for value, diagnosis in seq]


def getStatuses(item):
    value, diag = item
    substatuses = [symptom.status for symptom in diag.symptoms]
    return value, diag.status, substatuses


class PositiveFactory(SymptomFactory):
    title = "Positive"
    help = "Is positive."

    def __call__(self):
        context = self.context
        counter.inc()
        status = context > 0
        if status:
            description = self.help
        else:
            description = u"Is zero or negative."
        symptom = Symptom(self.title, self.help, status, description)
        return symptom


class GreaterThanOneFactory(SymptomFactory):
    title = "Greater than one"
    help = title

    def __call__(self):
        context = self.context
        status = context > 1
        if status:
            description = self.help
        else:
            description = u"Is smaller than one."
        symptom = Symptom(self.title, self.help, status, description)
        return symptom


class Filter(unittest.TestCase):

    def setUp(self):
        testing.setUp(self)
        provideAdapter(Diagnosis, [int], IDiagnosis)
        provideSubscriptionAdapter(
                PositiveFactory, [int], ISymptomFactory)
        provideSubscriptionAdapter(
                GreaterThanOneFactory, [int], ISymptomFactory)
        counter.clear()

    def tearDown(self):
        testing.tearDown(self)

    def testTrueFirst(self):
        from collective.jekyll.browser.filter import DiagnosisFilter

        values = [1, 2, 3, 4, 5, -1, -2, -3, -4, -5]

        filter = DiagnosisFilter(values, 10)

        self.assertEquals(getStatuses(filter[0]), (1, False, [True, False]))
        self.assertEquals(counter.value, 1)

        self.assertEquals(getValues(filter[:4]), [1, -1, -2, -3])
        self.assertEquals(counter.value, 8)

        self.assertEquals(getValues(filter[4:7]), [-4, -5, 2])
        self.assertEquals(counter.value, 10)

        self.assertEquals(getStatuses(filter[5]), (-5, False, [False, False]))
        self.assertEquals(counter.value, 10)

        self.assertEquals(getValues(filter[-3:]), [3, 4, 5])
        self.assertEquals(counter.value, 10)

        self.assertEquals(getStatuses(filter[9]), (5, True, [True, True]))

    def testFalseFirst(self):
        from collective.jekyll.browser.filter import DiagnosisFilter

        values = [-1, -2, -3, -4, -5, 1, 2, 3, 4, 5]

        filter = DiagnosisFilter(values, 10)

        self.assertEquals(getStatuses(filter[0]), (-1, False, [False, False]))
        self.assertEquals(counter.value, 1)

        self.assertEquals(getValues(filter[:4]), [-1, -2, -3, -4])
        self.assertEquals(counter.value, 4)

        self.assertEquals(getValues(filter[4:7]), [-5, 1, 2])
        self.assertEquals(counter.value, 10)

        self.assertEquals(getStatuses(filter[5]), (1, False, [True, False]))
        self.assertEquals(counter.value, 10)

        self.assertEquals(getValues(filter[-3:]), [3, 4, 5])
        self.assertEquals(counter.value, 10)

        self.assertEquals(getStatuses(filter[9]), (5, True, [True, True]))

    def testMixed(self):
        from collective.jekyll.browser.filter import DiagnosisFilter

        values = [-1, 1, -2, 2, -3, 3, -4, 4, -5, 5]

        filter = DiagnosisFilter(values, 10)

        self.assertEquals(getStatuses(filter[0]), (-1, False, [False, False]))
        self.assertEquals(counter.value, 1)

        self.assertEquals(getValues(filter[:4]), [-1, 1, -2, -3])
        self.assertEquals(counter.value, 5)

        self.assertEquals(getValues(filter[4:7]), [-4, -5, 2])
        self.assertEquals(counter.value, 10)

        self.assertEquals(getStatuses(filter[5]), (-5, False, [False, False]))
        self.assertEquals(counter.value, 10)

        self.assertEquals(getValues(filter[-3:]), [3, 4, 5])
        self.assertEquals(counter.value, 10)

        self.assertEquals(getStatuses(filter[9]), (5, True, [True, True]))