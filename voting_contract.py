from pyteal import *

class Poll:
    class Variables:
        #global
        id = Bytes("ID")
        image = Bytes("IMAGE")
        description = Bytes("DESCRIPTION")
        owner = Bytes("OWNER")
        option1 = Bytes("OPTION1")
        count1 = Bytes("COUNT1")
        option2 = Bytes("OPTION2")
        count2 = Bytes("COUNT2")
        option3 = Bytes("OPTION3")
        count3 = Bytes("COUNT3")
        
        #local
        voted = Bytes("VOTED")#if 1, user already voted

    class AppMethods:
        #Method used for a voting. Voters can vote only once per Poll.
        vote = Bytes("vote")
        #The Poll creator is ending the voting process and declaring the winner
        # declare_winner = Bytes("declare_winner")

    def application_creation(self):
        return Seq([
            #Asserts
            Assert(Txn.application_args.length() == Int(6)),
            Assert(Txn.note() == Bytes("voting-system:uv1")),
            
            #Global storage
            App.globalPut(self.Variables.id, Txn.application_args[0]),
            App.globalPut(self.Variables.image, Txn.application_args[1]),
            App.globalPut(self.Variables.description, Txn.application_args[2]),
            App.globalPut(self.Variables.option1, Txn.application_args[3]),
            App.globalPut(self.Variables.option2, Txn.application_args[4]),
            App.globalPut(self.Variables.option3, Txn.application_args[5]),
            App.globalPut(self.Variables.owner, Txn.sender()),
            App.globalPut(self.Variables.count1, Int(1)),
            App.globalPut(self.Variables.count2, Int(0)),
            # App.globalPut(self.Variables.count3, Int(0)),

            #Local storage
            # App.localPut(Int(0), self.Variables.voted, Int(0)),

            Approve()
        ])

    def vote(self):
        option = Txn.application_args[1]
        #Determine which option count should be increased
        update_state = Seq(
            Cond(
                [option == App.globalGet(self.Variables.option1), App.globalPut(self.Variables.count1, App.globalGet(self.Variables.count1) + Int(1))],
                [option == App.globalGet(self.Variables.option2), App.globalPut(self.Variables.count2, App.globalGet(self.Variables.count2) + Int(1))],
                [option == App.globalGet(self.Variables.option3), App.globalPut(self.Variables.count3, App.globalGet(self.Variables.count3) + Int(1))],
            ),
            Approve()
        )
        return Seq(
            # Assert(
            #     And(
            #         #check if number of arguments is correct
            #         # Txn.application_args.length() == Int(2),
            #         #check if user can vote (haven't already voted)
            #         # App.localGet(Txn.sender(), self.Variables.voted) == Int(0),
            #         #creator can't vote on its own poll
            #     )
            # ),
            update_state,
        )

    def application_start(self):
        return Cond(
            #If the app is not initialised yet / app_id == 0, then initialise it.
            [Txn.application_id() == Int(0), self.application_creation()],
            [Txn.on_completion() == OnComplete.DeleteApplication, self.application_deletion()],
            [Txn.application_args[0] == self.AppMethods.vote, self.vote()]
        )

    def application_deletion(self):
        return Return(Txn.sender() == Global.creator_address())

    def approval_program(self):
        return self.application_start()

    def clear_program(self):
        return Return(Int(1))