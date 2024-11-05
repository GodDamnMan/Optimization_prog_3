class NotApplicableError(Exception):
    pass

class NotBalancedError(Exception):
    pass




class TransportationModel:
    def __init__(self, supply:list, costs:list, demand:list, what_to_print:str = 'solution'):
        self.supply = supply
        self.costs = costs
        self.demand = demand
        self.what_to_print = what_to_print
        self.check()

        self.max_length = max([len(str(i)) for i in self.supply])
        self.max_length = max([self.max_length] + [len(str(i)) for i in self.demand])
        self.max_length = max([self.max_length] + [len(str(i)) for j in self.costs for i in j])
        self.formatting = '{:'+str(self.max_length) + '}'

        self.solution = [[0 for _ in range(len(self.costs[0]))] for _ in range(len(self.costs))]

    def check(self):
        if len(self.supply) != len(self.costs):
            raise NotApplicableError
        if len(self.demand) != len(self.costs[0]):
            raise NotApplicableError
        if any([len(self.costs[i]) != len(self.costs[i + 1]) for i in range(len(self.costs) - 1)]):
            raise NotApplicableError
        
        if sum(self.demand) != sum(self.supply):
            raise NotBalancedError
        
    def __print(self, what, name):
        ind = 0
        print('======================================')
        print(name)
        for i in what:
            for j in i:
                print(self.formatting.format(j), end=' ')
            print(self.formatting.format(self.supply[ind]))
            ind += 1
        for i in self.demand:
            print(self.formatting.format(i), end=' ')
        print()

    def __print_debug(self, what, name):
        ind = 0
        print('======================================')
        print(name)
        for i in what:
            for j in i:
                print(self.formatting.format(j), end=' ')
            print(self.formatting.format(self.supply[ind]))
            ind += 1
        for i in self.demand:
            print(self.formatting.format(i), end=' ')
        print()

    def print_init(self):
        self.__print(self.costs, "initial")
        
    def print_solution(self):
        self.solve()
        self.__print(self.solution, self.what_to_print)
        
        final_cost = 0
        for i in range(len(self.solution)):
            for j in range(len(self.solution[0])):
                final_cost += self.solution[i][j] * self.costs[i][j]
        print(f"aproximated optimum = {final_cost}")

    def solve(self):
        pass

class NordWestModel(TransportationModel):
    def __init__(self, supply:list = None, costs:list = None, demand:list = None, transportation_model:TransportationModel = None):
        if transportation_model == None:
            super().__init__(supply, costs, demand, what_to_print="Nord west solution")
        else:
            super().__init__(transportation_model.supply, transportation_model.costs, transportation_model.demand, what_to_print="Nord west solution")


    def solve(self):
        i = 0
        j = 0
        while True:
            if i == len(self.solution) or j == len(self.solution[0]):
                break
            
            supply_occupied = sum(self.solution[i])
            demand_satisfied = sum([self.solution[el][j] for el in range(len(self.solution))])

            if self.supply[i] - supply_occupied  < self.demand[j] - demand_satisfied:
                self.solution[i][j] = self.supply[i] - supply_occupied
                i += 1
                continue

            else:
                self.solution[i][j] = self.demand[j] - demand_satisfied
                j += 1
                continue

class VogelModel(TransportationModel):
    def __init__(self, supply:list = None, costs:list = None, demand:list = None, transportation_model:TransportationModel = None):
        if transportation_model == None:
            super().__init__(supply, costs, demand, what_to_print="Vogel's solution")
        else:
            super().__init__(transportation_model.supply, transportation_model.costs, transportation_model.demand, what_to_print="Vogel's solution")

    def solve(self):
        self.mutable_costs = [el.copy() for el in self.costs]
        while True:
            max_difference_of_mins = -1
            where_min = -1
            is_min_supply = True

            for i in range(len(self.mutable_costs)):
                temp = self.__diff_of_smallest(self.mutable_costs[i])
                if max_difference_of_mins < temp:
                    max_difference_of_mins = temp
                    where_min = i
            
            for i in range(len(self.mutable_costs[0])):
                temp = self.__diff_of_smallest([self.mutable_costs[el][i] for el in range(len(self.mutable_costs))])
                if max_difference_of_mins < temp:
                    max_difference_of_mins = temp
                    where_min = i
                    is_min_supply = False

            if(max_difference_of_mins == -1):
                return

            if is_min_supply:
                i = where_min
                j = self.__ind_of_smallest(self.mutable_costs[i])
                self.__occupie(i, j)
                
            else:
                j = where_min
                i = self.__ind_of_smallest([self.mutable_costs[el][j] for el in range(len(self.mutable_costs))])
                self.__occupie(i, j)
            
            

    def __occupie(self, i, j):
        supply_occupied = sum(self.solution[i])
        demand_satisfied = sum([self.solution[el][j] for el in range(len(self.solution))])

        if self.supply[i] - supply_occupied  < self.demand[j] - demand_satisfied:
            self.solution[i][j] = self.supply[i] - supply_occupied
            self.__del_row_column(i, True)
        else:
            self.solution[i][j] = self.demand[j] - demand_satisfied
            self.__del_row_column(j, False)


    def __del_row_column(self, i, is_row):
        if is_row:
            for j in range(len(self.mutable_costs[0])):
                self.mutable_costs[i][j] = float('inf')
        else:
            for j in range(len(self.mutable_costs)):
                self.mutable_costs[j][i] = float('inf')


    def __diff_of_smallest(self, a:list):
        min1, min2 = float('inf'), float('inf')

        for i in a:
            if i <= min1:
                min1, min2 = i, min1
                continue
            if i < min2:
                min2 = i
                continue
        return min2 - min1 if (min1 != float('inf') or min2 != float('inf')) else -1
            

    def __ind_of_smallest(self, a:list):
        min1 = float('inf')
        min_index = -1
        for i in range(len(a)):
            if a[i] < min1:
                min1 = a[i]
                min_index = i
                
        return min_index

class RusselsModel(TransportationModel):
    def __init__(self, supply:list = None, costs:list = None, demand:list = None, transportation_model:TransportationModel = None):
        if transportation_model == None:
            super().__init__(supply, costs, demand, what_to_print="Russell's solution")
        else:
            super().__init__(transportation_model.supply, transportation_model.costs, transportation_model.demand, what_to_print="Russell's solution")

    def solve(self):
        #TODO
        while True:
            return

    def __occupie(self, i, j):
        supply_occupied = sum(self.solution[i])
        demand_satisfied = sum([self.solution[el][j] for el in range(len(self.solution))])

        if self.supply[i] - supply_occupied  < self.demand[j] - demand_satisfied:
            self.solution[i][j] = self.supply[i] - supply_occupied
            self.__del_row_column(i, True)
        else:
            self.solution[i][j] = self.demand[j] - demand_satisfied
            self.__del_row_column(j, False)


    def __del_row_column(self, i, is_row):
        if is_row:
            for j in range(len(self.mutable_costs[0])):
                self.mutable_costs[i][j] = float('inf')
        else:
            for j in range(len(self.mutable_costs)):
                self.mutable_costs[j][i] = float('inf')


n = TransportationModel([140,180,160], [[2,3,4,2,4], [8,4,1,4,1], [9,7,3,7,2]], [60,70,120,130,100])
n.print_init()

NordWestModel(transportation_model = n).print_solution()

VogelModel(transportation_model = n).print_solution()

a = RusselsModel(transportation_model = n)
a.print_solution