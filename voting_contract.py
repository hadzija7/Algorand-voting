from pyteal import *

class Poll:
    class Variables:
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

    class AppMethods:
        #Method used for a voting. Voters can vote only once per Poll.
        vote = Bytes("vote")
        #The Poll creator is ending the voting process and declaring the winner
        # declare_winner = Bytes("declare_winner")

    def application_creation(self):
        return Seq([
            Assert(Txn.application_args.length() == Int(6)),
            Assert(Txn.note() == Bytes("voting-system:uv1")),
            App.globalPut(self.Variables.id, Txn.application_args[0]),
            App.globalPut(self.Variables.image, Txn.application_args[1]),
            App.globalPut(self.Variables.description, Txn.application_args[2]),
            App.globalPut(self.Variables.option1, Txn.application_args[3]),
            App.globalPut(self.Variables.option2, Txn.application_args[4]),
            App.globalPut(self.Variables.option3, Txn.application_args[5]),
            App.globalPut(self.Variables.owner, Txn.sender()),
            Approve()
        ])

    def vote(self):
        #option = Txn.application_args[1]
        #Check if a user has already voted
        can_vote = And(
            Int(1) == Int(1)
        )

        #Determine which option count should be increased
        update_state = Seq(
            # If(
            #     option == Bytes("OPTION1"),
            #     App.globalPut(self.Variables.count1, App.globalGet(self.Variables.count1) + Int(1)),
            # ),
            # If(option == "OPTION1").Then(
            #     App.globalPut(self.Variables.count1, App.globalGet(self.Variables.count1) + 1),
            # ).ElseIf(option == "OPTION2").Then(
            #     App.globalPut(self.Variables.count2, App.globalGet(self.Variables.count2) + 1),
            # ).ElseIf(option == "OPTION3").Then(
            #     App.globalPut(self.Variables.count3, App.globalGet(self.Variables.count3) + 1),
            # ).Else(
            #     Reject()
            # )
            Approve()
        )

        return If(can_vote).Then(update_state).Else(Reject())
        # return update_state

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


    # def buy(self):
    #     count = Txn.application_args[1]
    #     valid_number_of_transactions = Global.group_size() == Int(2)

    #     valid_payment_to_seller = And(
    #         Gtxn[1].type_enum() == TxnType.Payment,
    #         Gtxn[1].receiver() == Global.creator_address(),
    #         Gtxn[1].amount() == App.globalGet(self.Variables.price) * Btoi(count),
    #         Gtxn[1].sender() == Gtxn[0].sender(),
    #     )

    #     can_buy = And(valid_number_of_transactions,
    #                   valid_payment_to_seller)

    #     update_state = Seq([
    #         App.globalPut(self.Variables.sold, App.globalGet(self.Variables.sold) + Btoi(count)),
    #         Approve()
    #     ])

    #     return If(can_buy).Then(update_state).Else(Reject())