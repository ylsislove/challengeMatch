# -*- coding:utf-8 -*-


import Ano_Stage


class Mode:

    def __init__(self):

        self.stage = Ano_Stage.Stage()
        self.controller = self.stage.fnset.controller
        self.command = self.controller.command
        self.port = self.command.receiver.base.port
        self.command.receiver.receive()

    def control(self, cmd):
        if cmd == "takeoff":
            self.command.takeoff()
        elif cmd == "land":
            self.command.land()
        elif cmd == "surLand":
            self.command.surLand()
        else:
            self.command.setCommand(cmd, 10, 10)
