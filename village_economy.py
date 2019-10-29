def Village_economy_model(vmodel):

    from pyomo.environ import Param, RangeSet, NonNegativeReals, Var, Set, Objective, maximize

    # Time parameters
    vmodel.Years = Param() # Number of years of the project

    #supporting sets lists and tuples
    tupsec = ("Trad", "Modern")
    tupvec = ("El", "Modern_NEl","Trad_NEl")

    # SETS
    vmodel.years = RangeSet(1, vmodel.Years)
    vmodel.sectors = Set(dimen=1, initialize = tupsec )
    vmodel.envector = Set(dimen=1, initialize = tupvec )

    #PARAMETERS
    vmodel.delta = Param(vmodel.sectors)
    vmodel.endelta = Param()
    vmodel.engamma = Param(vmodel.sectors)
    vmodel.gamma = Param(vmodel.sectors)
    vmodel.disc_rate = Param()
    vmodel.enel = Param(vmodel.sectors,vmodel.envector)
    vmodel.speclab = Param(vmodel.envector)
    vmodel.speccap = Param(vmodel.envector)
    vmodel.specvar = Param(vmodel.envector)
    vmodel.workingpeople = Param()
    vmodel.workinghoursyr = Param()

    #VARIABLES
    vmodel.Labor=Var(vmodel.years,vmodel.sectors,Within=NonNegativeReals)
    vmodel.Capital=Var(vmodel.years,vmodel.sectors)
    vmodel.Investment=Var(vmodel.years,vmodel.sectors,Within=NonNegativeReals)
    vmodel.Output=Var(vmodel.years,vmodel.sectors,Within=NonNegativeReals)
    vmodel.Consumption=Var(vmodel.years,Within=NonNegativeReals)
    vmodel.Utility=Var()

    #ENERGY VARIABLES
    vmodel.Enlabor=Var(vmodel.years,vmodel.envector,Within=NonNegativeReals)  
    vmodel.Encapital=Var(vmodel.years,vmodel.envector)
    vmodel.Eninvestment=Var(vmodel.years,vmodel.envector)
    vmodel.Varcost=Var(vmodel.years,vmodel.envector)
    vmodel.Energy=Var(vmodel.years,vmodel.envector,Within=NonNegativeReals)
    vmodel.Energyinput=Var(vmodel.years,vmodel.sectors,Within=NonNegativeReals)



def Village_economy_res(vmodel,datapath=''):

    #COSTRAINTS

    def Outputeq(vmodel,yr,sec):

        return vmodel.Output[yr,sec] = en_gamma[sec]*vmodel.Energyinput[yr,sec] + (1-en_gamma[sec])*( vmodel.Labor[yr,sec]^gamma[sec] * vmodel.Capital[yr,sec]^(1-gamma[sec]) )

    vmodel.Outputeq = Constraint(vmodel.years,vmodel.sectors,rule=Outputeq)

    def Energyeq(vmodel,yr,envec):

        return vmodel.Energy[yr,envec] = min( vmodel.Enlabor[yr,envec]/speclab[envec], vmodel.Encapital[yr,envec]/speccap[envec], vmodel.Varcost[yr,envec]/specvar[envec] )

    vmodel.Energyeq = Constraint(vmodel.years,vmodel.envector,rule=Energyeq)

    def Energyinputeq(vmodel,yr,sec):

        prod = 1
        for i in range vmodel.envector:
            prod = prod*vmodel.Energy[yr,i]^enel[sec,i]
        return vmodel.Energyinput[yr] = prod

    vmodel.Energyinputeq = Constraint(vmodel.years,vmodel.sectors,rule=Energyinputeq)

    def Laboreq(vmodel,yr):

        return sum(vmodel.Labor[yr,sec] for sec in range vmodel.sectors) + sum(vmodel.Enlabor[yr,envec] for envec in range vmodel.envector) <= vmodel.workingpeople*vmodel.workinghoursyr

    vmodel.Laboreq = Constraint(vmodel.years,rule=Laboreq)

    def Capitaleq(vmodel,yr,sec):

        return vmodel.Capital[yr+1,sec] = (1-vmodel.delta[sec])*vmodel.Capital[yr,sec] +  vmodel.Investment[yr,sec]

    vmodel.Capitaleq = Constraint(vmodel.years,vmodel.sectors,rule=Capitaleq)

    def Encapitaleq(vmodel,yr,envec):

        return vmodel.Encapital[yr+1,envec] = (1-vmodel.endelta)*vmodel.Encapital[yr,envec] +  vmodel.Eninvestment[yr,envec]

    vmodel.Encapitaleq = Constraint(vmodel.years,vmodel.envector,rule=Encapitaleq)

    def Consumptioneq(vmodel,yr):

        return vmodel.Consumption[yr] = sum(vmodel.Output[yr,sec] for sec in range vmodel.sectors) - sum(vmodel.Varcost for ) sum(vmodel.Investment[yr,sec] for sec in range vmodel.sectors) - sum(vmodel.Eninvesment[yr,envec] for envec in range vmodel.envector)

    vmodel.Consumptioneq = Constraint(vmodel.years,rule=Consumptioneq)

    def Utilityeq(vmodel):

        return vmodel.Utility = sum(vmodel.Consumption[yr]*(1+disc_rate[yr])^(-yr) for yr in range vmodel.years)

    vmodel.Utilityeq = Constraint(rule=Utilityeq)

    def Objfunc(vmodel):

        return vmodel.Utility

    vmodel.OBJ = Objective(rule=Objfunc,sense=maximize)


    instance = model.create_instance(datapath) 
    opt = SolverFactory('')    
    results = opt.solve(instance, tee=True) 
    instance.solutions.load_from(results) 

    return instance

vmodel = Abstractmodel()
Village_economy_model(model)
instance = Village_economy_res(model)
