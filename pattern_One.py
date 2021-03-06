import ast
import astor
from z3 import *

class OneNodeSearcher():
    is_continuous = False # 連続していることを判定する
    # node: 現在のノード,count: ifの位置関係を確認するための変数, previous: 前までに検出された条件式を格納する辞書型変数, conditions:
    def one_search(self, node, count = 1, previous = {}, conditions = None, lineno = None):
        if lineno is None:
            lineno = []
        if conditions is None:
            conditions = []
        if type(node) is ast.If: # まず起点となるif文を探す
            # キー"count - 1"の要素がpreviousにあるとき，つまりこのifの直前にifがある場合
            if count - 1 in previous:
                # previous[count - 1]がconditionsの中にないとき（条件の重複を防ぐため）
                if previous[count - 1] not in conditions:

                    # そのprevious[count - 1]を末尾に追加
                    conditions.append(previous.pop(count - 1))
                    lineno.append(previous.pop(1 - count))

                # conditionsの末尾に現在のcountの条件文を追加
                conditions.append(node.test)
                lineno.append(node.lineno)

                # 連続していることを判定する
                self.is_continuous = True
            else:
                self.process_when_exiting_if(conditions, lineno)
                conditions = []
                lineno = []

            # previousにキーをcountとした条件文のリストを登録することによって一時的に記憶
            previous[count] = node.test
            previous[-count] = node.lineno
        else:
            self.process_when_exiting_if(conditions, lineno)
            conditions = []
            lineno = []
        cnt = 0
        for child in ast.iter_child_nodes(node):
            # 子ノードに対して再帰する
            cnt = cnt + 1
            self.one_search(child, cnt, previous, conditions, lineno)

    def process_when_exiting_if(self, conditions, lineno):
        # ifのカウントから抜けたとき
        if self.is_continuous:
            # 以下連続が切れた時から判定処理を行う

            # z3処理結果格納用の変数定義
            z3var = {}
            z3_list = []

            # 条件式ごとに処理をする
            for i in conditions:
                # 条件式に含まれる変数をz3用にフォーマット
                var_list = self.search_variable_name(i)
                for j in range(len(var_list)):
                    z3var[var_list[j]] = Int(var_list[j])

                # z3を用いて条件文の具体的な表現を解析し，リストに格納する
                result, eq_flag = self.expr_investigate(i,z3var)
                if type(result) is list:
                    result = list(set(result))
                z3_list.append(result)
                z3var = {}
            # 解析結果から冗長なコードの条件に当てはまるか調べる
            self.conditions_analyze(z3_list, lineno, eq_flag)

            self.is_continuous = False

    def conditions_analyze(self, condition_list, lineno, eq_flag):
        """
        解析結果から冗長なコードの条件に当てはまるか調べる
        """
        if len(condition_list) != 1:
            if eq_flag:
                t = Tactic("simplify")
            else:
                t = Then(Tactic("solve-eqs"),Tactic('simplify'))
            while len(condition_list) != 1:
                tmp = condition_list.pop(0)
                if type(tmp) is list:
                    for i in range(len(tmp)):
                        tmp[i] = t(Not(tmp[i])).as_expr()
                    g = tmp
                else:
                    g = t(Not(self.conditions_integrate(tmp))).as_expr()
                result = []
                for i in condition_list:
                    if type(g) is list:
                        for k in g:
                            if type(i) is list:
                                tmp = self.list_analyze(i, k)
                                if tmp != None:
                                    if not tmp in result:
                                        result.append(tmp)
                                        print("line:{0} ~ line:{1}, condition \"{2}\" may be simplified by elif-statement".format(lineno[0], lineno[-1], result))
                    else:
                        if type(i) is list:
                            tmp = self.list_analyze(i, g)
                            if tmp != None:
                                if not tmp in result:
                                    result.append(tmp)
                                    print("line:{0} ~ line:{1}, condition \"{2}\" may be simplified by elif-statement".format(lineno[0], lineno[-1], result))


    def conditions_integrate(self, conditions, g = True):
        """
        docstring
        """
        if type(conditions) is list:
            for i in conditions:
                g = self.conditions_integrate(i, g)
            return g
        else:
            return And(g, conditions)
    def list_analyze(self, i, g):
        for j in i:
            if type(j) is list:
                self.list_analyze(j, g)
            else:
                if j == g:
                    return j

    def search_variable_name(self, node, variables = None):
        if variables is None:
            variables = []
        """
        プログラム内で使われている変数の名前を検索する関数
        """
        if type(node) is ast.BoolOp:
            temporary = []
            for i in node.values:
                tem = self.search_variable_name(i, temporary)
                temporary = temporary + tem
            return temporary
        elif type(node) is ast.Compare:
            tmp1_list = self.search_variable_name(node.left, variables)
            for j in node.comparators:
                tmp1_list.extend(self.search_variable_name(j, variables))
            return tmp1_list
        elif type(node) is ast.BinOp:
            return variables + self.search_variable_name(node.left) + self.search_variable_name(node.right)
        elif type(node) is ast.Name :
            tmp_list = []
            if node.id not in variables:
                tmp_list = variables + [node.id]
            return tmp_list
        elif type(node) is ast.UnaryOp:
            return self.search_variable_name(node.operand, variables)
        elif type(node) is ast.Constant:
            return []
        else:
            print("unknown class")
            return variables
    def expr_investigate(self, i, z3var):

        """
        どのような条件かによって処理する
        """
        # z3用の変数定義
        g  = Goal()
        # 演算子を用いている場合
        if type(i) is ast.Compare:
            op = type(i.ops[0])
            if op is ast.Gt:
                g.add(z3var[i.left.id].__gt__(i.comparators[0].value))
            elif op is ast.LtE:
                g.add(Not(z3var[i.left.id].__gt__(i.comparators[0].value)))
            elif op is ast.Eq:
                g.add(z3var[i.left.id].__eq__(i.comparators[0].value))
            return g[0]

        elif type(i) is ast.BoolOp:
            conditions, bool_list, eq_flag = self.bool_analyze(i, z3var)
            if eq_flag:
                t = Tactic("simplify")
            else:
                t = Then(Tactic("solve-eqs"),Tactic('simplify'))
            if len(conditions) > 1:
                if str(And(conditions[0], conditions[1])).startswith("And"):
                    result = []
                    for k in conditions:
                        result.append(t(k).as_expr())
                    return result, eq_flag
                else:
                    return t(And(conditions[0], conditions[1])).as_expr(), eq_flag
            return conditions, eq_flag


    def bool_analyze(self, i, z3var, bool_list = [], conditions = None, eq_flag = False):
        """
        docstring
        """
        if conditions is None:
            conditions = []
        boolean = type(i.op)

        if boolean is ast.And:
            # ANDのとき
            # andであることをリストに記憶しておく
            bool_list.append(i.op)
            for k in i.values:
                if type(k) is ast.Compare:
                    # 演算子を用いている場合
                    op = type(k.ops[0])
                    if op is ast.Gt:
                        conditions.append(z3var[k.left.id].__gt__(k.comparators[0].value))
                    elif op is ast.Lt:
                        conditions.append(z3var[k.left.id].__lt__(k.comparators[0].value))
                    elif op is ast.LtE:
                        conditions.append(Not(z3var[k.left.id].__gt__(k.comparators[0].value)))
                    elif op is ast.GtE:
                        conditions.append(Not(z3var[k.left.id].__lt__(k.comparators[0].value)))
                    elif op is ast.NotEq:
                        conditions.append(Not(z3var[k.left.id].__eq__(k.comparators[0].value)))
                elif type(k) is ast.BoolOp:
                    conditions, bool_list, eq_flag = self.bool_analyze(k, z3var, bool_list, conditions)
                elif type(k) is ast.UnaryOp:
                    conditions, bool_list, eq_flag = self.bool_analyze(k.operand, z3var, bool_list, conditions)
                    if eq_flag:
                        t = Tactic("simplify")
                    else:
                        t = Then(Tactic("solve-eqs"),Tactic('simplify'))
                    conditions.append(t(Not(conditions[0])).as_expr())
        elif boolean is ast.Or:
            bool_list.append(i.op)
            for k in i.values:
                if type(k) is ast.Compare:
                    # 演算子を用いている場合
                    op = type(k.ops[0])
                    if op is ast.Gt:
                        conditions.append(z3var[k.left.id].__gt__(k.comparators[0].value))
                    elif op is ast.Lt:
                        conditions.append(z3var[k.left.id].__lt__(k.comparators[0].value))
                    elif op is ast.LtE:
                        conditions.append(Not(z3var[k.left.id].__gt__(k.comparators[0].value)))
                    elif op is ast.GtE:
                        conditions.append(Not(z3var[k.left.id].__lt__(k.comparators[0].value)))
                    elif op is ast.Eq:
                        eq_flag = True
                        conditions.append(z3var[k.left.id].__eq__(k.comparators[0].value))
                    elif op is ast.NotEq:
                        conditions.append(Not(z3var[k.left.id].__eq__(k.comparators[0].value)))
                elif type(k) is ast.BoolOp:
                    conditions, bool_list, eq_flag = self.bool_analyze(i, z3var, bool_list, conditions, eq_flag)
            if eq_flag:
                t = Tactic("simplify")
            else:
                t = Then(Tactic("solve-eqs"),Tactic('simplify'))
            conditions[0] = t(Not(And(Not(conditions[0]), Not(conditions[1])))).as_expr()
            conditions.pop(1)
        return conditions, bool_list, eq_flag
def main():
    """
    main
    """
    # file_name = r'c:\Users\maru\Documents\Github\marui_novice_linter\tryz3.py'
    file_name = r'c:\Users\maru\Documents\Github\marui_novice_linter\pydat.py'
    with open(file_name, 'r', encoding="utf-8_sig") as sourse_file:
        source = sourse_file.read()

    tree = ast.parse(source, file_name)

    # FiveSixNodeVisitor().visit(tree)
    # TwoNodeVisitor().visit(tree)
    OneNodeSearcher().one_search(tree)
if __name__ == '__main__':
    main()