class NotApplicableError(Exception):
    pass

class NotBalancedError(Exception):
    pass




class TransportationModel:
    def __init__(self, supply:list, costs:list, demand:list, whoes_solution:str = 'solution'):
        self.supply = supply
        self.costs = costs
        self.demand = demand
        self.whoes_solution = whoes_solution
        self.check()

        self.max_length = max([len(str(i)) for i in self.supply])
        self.max_length = max([self.max_length] + [len(str(i)) for i in self.demand])
        self.max_length = max([self.max_length] + [len(str(i)) for j in self.costs for i in j])
        self.max_length += 1

        self.formatting = '{:'+str(self.max_length) + '}'   
        
        for i in range(len(self.costs)):
            for j in range(len(self.costs[0])):
                if self.costs[i][j] == 'M':
                    self.costs[i][j] = float("inf")

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
        
    def __print(self, table, whoes_solution):
        ind = 0
        print('\n\n')
        print('=' * (self.max_length + 1) * (len(self.demand) + 1))
        print(whoes_solution)
        for i in table:
            for j in i:
                print(self.formatting.format(j), end=' ')
            print(self.formatting.format(self.supply[ind]))
            ind += 1
        for i in self.demand:
            print(self.formatting.format(i), end=' ')
        print()


    def __print_debug(self, table):
        self.__print(table, 'debug')


    def print_init(self):
        self.__print(self.costs, 'initial')
        
    def print_solution(self):
        self.solve()
        self.__print(self.solution, self.whoes_solution)
        
        final_cost = 0
        inf_cost = 0
        for i in range(len(self.solution)):
            for j in range(len(self.solution[0])):
                if self.costs[i][j] == float('inf'):
                    inf_cost += self.solution[i][j]
                else:
                    final_cost += self.solution[i][j] * self.costs[i][j]

        print(f"\naproximated optimum = {final_cost}", end=' ')
        if inf_cost != 0:
            print(f'+ {inf_cost} inf',end='')
        print()
        


    def solve(self):
        pass

class NordWestModel(TransportationModel):
    def __init__(self, supply:list = None, costs:list = None, demand:list = None, transportation_model:TransportationModel = None):
        if transportation_model == None:
            super().__init__(supply, costs, demand, whoes_solution="Nord west solution")
        else:
            super().__init__(transportation_model.supply, transportation_model.costs, transportation_model.demand, whoes_solution="Nord west solution")


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
            super().__init__(supply, costs, demand, whoes_solution="Vogel's solution")
        else:
            super().__init__(transportation_model.supply, transportation_model.costs, transportation_model.demand, whoes_solution="Vogel's solution")

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
            super().__init__(supply, costs, demand, whoes_solution = "Russell's solution")
        else:
            super().__init__(transportation_model.supply, transportation_model.costs, transportation_model.demand, whoes_solution="Russell's solution")

    def solve(self):
        self.mutable_costs = [el.copy() for el in self.costs]
        while True:
            max_of_rows = [max(i) for i in self.mutable_costs]
            max_of_columns = [max(i) for i in [[self.mutable_costs[el][j] for el in range(len(self.mutable_costs))] for j in range(len(self.mutable_costs[0]))]]
            
            min_delta = float('inf')
            min_i = -1
            min_j = -1
            for i in range(len(self.mutable_costs)):
                for j in range(len(self.mutable_costs[0])):
                    if self.mutable_costs[i][j] == -1:
                        continue
                    delta = self.mutable_costs[i][j] - max_of_rows[i] - max_of_columns[j]
                    if min_delta > delta:
                        min_delta = delta
                        min_i, min_j = i, j
            
            if min_i == -1:
                return
            
            self.__occupie(min_i,min_j)
            



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
                self.mutable_costs[i][j] = -1
        else:
            for j in range(len(self.mutable_costs)):
                self.mutable_costs[j][i] = -1





def main():
    n = TransportationModel([50, 60, 50, 50], [[16,16,13,22,17], [14,14,13,19,15], [19,19,20,23,'M'], ['M',0,'M',0,0]], [30,20,70,30,60])
    n.print_init()

    NordWestModel(transportation_model = n).print_solution()
    VogelModel(transportation_model = n).print_solution()
    RusselsModel(transportation_model = n).print_solution()


main()