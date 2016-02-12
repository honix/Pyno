from utils import sum_coma


class Processor(object):
    # Processor is a engine of pyno, there functions defines
    # and outputs calculates

    def init_processor(self):
        self.proc_result = None
        self.func = None

        self.gen_output = {}

        self.need_update = True
        self.problem = False

        self.local_space = {}

    def processor(self, space):
        # Called every frame

        if self.proc_result and not self.need_update:
            return self.proc_result

        self.problem = False

        # check all in-connections, get results and gave names of in-puts
        gen_inputs = []
        for connection in self.connectedTo:
            try:
                inputs = connection['output']['node'].processor(space)
                data = inputs[connection['output']['put']['name']]
            except:
                self.er_label.text = 'Cant read input'
                self.problem = True
                continue
            gen_inputs.append((connection['input']['put']['name'], data))

        # exec that new function and put it in to space
        if self.need_update:
            try:  # avoid name repeats
                eval(self.name)
                self.er_label.text = ('%s already exist, please rename'
                                      % self.name)
                self.problem = True
            except:
                try:
                    space['S'] = self.local_space
                    exec(self.code, space)
                    self.func = eval('%s' % self.name, space)
                except Exception as ex:
                    if not self.problem:
                        self.er_label.text = str(ex)
                    self.problem = True
                else:
                    self.need_update = False

        # run-time mode: just get inputs and put in function
        else:
            try:
                space['S'] = self.local_space
                result = eval('self.func({})'.format(sum_coma(gen_inputs)))
            except Exception as ex:
                if not self.problem:
                    self.er_label.text = str(ex)
                self.problem = True

            # build output
            for output in self.outputs:
                try:
                    if (result and len(self.outputs) > 1
                    and isinstance(result, tuple)):
                        r = result[self.outputs.index(output)]
                        self.gen_output[output] = r  # tuple output
                    else:
                        self.gen_output[output] = result  # one output
                except Exception as ex:
                    if not self.problem:
                        self.er_label.text = str(ex)
                    self.problem = True

                self.proc_result = self.gen_output
        return self.gen_output