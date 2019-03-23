class TestOrderInnerOuter:
    def __init__(self):
        self.orders = {
            '1': {'inner': ['2'], 'outer': ['0']},
            '2': {'inner': ['3'], 'outer': ['1']},
            '3': {'inner': ['4'], 'outer': ['2']},
            '4': {'inner': ['4', '5'], 'outer': ['3']},
            '5': {'inner': ['6'], 'outer': ['4']},
            '6': {'inner': ['7'], 'outer': ['5']}
        }

    def _util_flatten(self, l):
        flat_l = [e for l_sub in l for e in l_sub]
        return flat_l

    def handle_branching(self):
        # start with unordered list
        unordered_list = ['2', '4', '1', '5']
        ordered_list = []
        #self.order_branches('3', ordered_list, unordered_list)
        print(ordered_list)

        tracker = set()
        l = self.order_without_repetitions('2', unordered_list, tracker)
        print(l)

    # third recursive attempt - avoid exceeding max depth!
    def order_without_repetitions(self, n, source_l, tracker):

        if n not in self.orders or n in tracker:
            return []
        
        tracker.add(n)

        # data
        inners = [
            inner for inner in self.orders[n]['inner']
            if inner not in tracker
        ]
        outers = [
            outer for outer in self.orders[n]['outer']
            if outer not in tracker
        ]

        # TODO: the base case
        if not (inners or outers):
            return [n]
        
        central_member = [n] if n in source_l else []

        # TODO: the recursion
        # /!\ Ns point both ways, an inner to its outer and an outer back to its inner
        inners_outers = [
            self.order_without_repetitions(outer, source_l, tracker) for outer in outers
        ] + central_member + [
            self.order_without_repetitions(inner, source_l, tracker) for inner in inners
        ]

        return self._util_flatten(inners_outers)

    # ns_2 = ['4', '2', '1', '5', '3']
    #
    # 3
    # -> 2... + 3 + 4...
    # [...outers] + n + [inners...]
    # -> 1 + 2 + 3 + 4 + 5
    #
    #
    # recursively appending to external list
    def order_branches(self, n, ordered_l, source_l):
        if n not in self.orders or n in ordered_l or n not in source_l: return
        outers = list(filter(lambda x: x not in ordered_l, self.orders[n]['outer']))
        inners = list(filter(lambda x: x not in ordered_l, self.orders[n]['inner']))
        [self.order_branches(inner, ordered_l, source_l) for inner in inners]
        ordered_l = [n] + ordered_l
        [self.order_branches(outer, ordered_l, source_l) for outer in outers]

    # recursive internal list creation
    def build_simple_order(self, e, d, source_ns, target_ns):
        if e not in d or e in target_ns:
            target_ns = target_ns
            return target_ns
        # intersection
        outers = [outer for outer in d[e]['outer'] if outer in source_ns and outer not in target_ns]
        inners = [inner for inner in d[e]['inner'] if inner in source_ns and inner not in target_ns]
        if not (inners or outers):
            target_ns = [e] + target_ns
            return target_ns
        target_ns = [
            item for item in [
                self.build_simple_order(outer, d, source_ns, target_ns) for outer in outers
            ] + [e] + [
                self.build_simple_order(inner, d, source_ns, target_ns) for inner in inners
            ]
        ] + target_ns
        return target_ns

orderer = TestOrderInnerOuter()
orderer.handle_branching()
