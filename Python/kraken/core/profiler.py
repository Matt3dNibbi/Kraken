"""Kraken - objects.profiler module.

Classes:
Profiler - Profiler Object.

"""
import time
import operator



class Profiler(object):
    """Kraken profiler object for debugging performance issues."""

    __instance = None

    class ProfilerItem(object):

        def __init__(self, label):
            super(Profiler.ProfilerItem, self).__init__()

            t = time.time()
            self.label = label
            self.start = t
            self.end = t
            self.children = []

        def addChild(self, item):
            self.children.append(item)

        def endProfiling(self):
            self.end = time.time()

    def __init__(self, label='Root'):
        super(Profiler, self).__init__()
        self.reset(label=label)

    def reset(self, label='Root'):
        """Resets the profiler for generating a new report

        Return:
        None

        """
        self.__roots = []
        self.__stack = []

    def push(self, label):
        """Adds a new child to the profiling tree and activates it.

        Return:
        None

        """

        item = Profiler.ProfilerItem(label)
        if len(self.__stack) == 0:
            self.__roots.append(item)
        else:
            self.__stack[-1].addChild(item)
        self.__stack.append(item)


    def pop(self):
        """Deactivates the current item in the tree and returns the profiler to the parent item

        Return:
        None

        """
        end = time.time()
        if len(self.__stack) == 0:
            raise Exception("Unable to close bracket. Pop has been called more times than push.") 
             
        self.__stack[-1].endProfiling()
        self.__stack.pop()
        
    def generateReport(self, listFunctionTotals=False):
        """Returns a report string containing all the data gathered turing profiling.

        Return:
        the json object

        """
        if len(self.__stack) != 0:
            raise Exception("Profiler brackets not closed properly. pop must be called for every call to push. Pop needs to be called another " + str(len(self.__stack)) + " times") 
        report = []
        report.append("--callstack--")
        functions = {}
        def reportItem(item, indent):
            duration = item.end - item.start
            report.append(indent + item.label + ' duration: ' + str(duration))
            if item.label not in functions:
                functions[item.label] = duration
            else:
                functions[item.label] += duration

            for childItem in item.children:
                reportItem(childItem, indent+'  ')

        for rootItem in self.__roots:
            reportItem(rootItem, '  ')

        if listFunctionTotals:
            report.append("--functions--")
            def reverse_numeric(x, y):
                return y < x
            sorted_fns = sorted(functions.items(), key=operator.itemgetter(1), cmp=reverse_numeric)
            for fn_tuple in sorted_fns:
                report.append(str(fn_tuple[1]) +': ' + fn_tuple[0])
        return '\n'.join(report)

    @classmethod
    def getInstance(cls):
        """This class method returns the singleton instance for the Profiler

        Return:
        The singleton instance.

        """

        if cls.__instance is None:
            cls.__instance = Profiler()

        return cls.__instance