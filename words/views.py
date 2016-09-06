from django.http import HttpResponse
from django.http import JsonResponse
from random import randint
import sqlite3

def index(request):
    #return HttpResponse("Hello, world. You're at the words index.")
    return get_word(request);

def get_word(request):

    op         = request.GET.get('op', 'FETCH');
    mode       = request.GET.get('mode', 'En2He');
    minId      = request.GET.get('minId', 0);
    maxId      = request.GET.get('maxId', 5000);
    maxRatio   = request.GET.get('maxRatio', 0.0);
    minVisits  = request.GET.get('minVisits', 3);
    onlyNew    = request.GET.get('onlyNew', False);
    method     = request.GET.get('method', 'random');
    maxRecords = request.GET.get('maxRecords', 1);
    id         = request.GET.get('id', 0);
    new_eng    = request.GET.get('new_eng', None);
    new_heb    = request.GET.get('new_heb', None);

    print("MMMMMMMMMMMMMMMMin VISITS = " + str(minVisits));
    if op == "FETCH":
        res = get_words_from_db(mode=mode, minId=minId, maxId=maxId, maxRatio=maxRatio, minVisits=minVisits, onlyNew=onlyNew, method=method, maxRecords=maxRecords);

        id             = res[0];
        english        = res[1];
        hebrew         = res[2];
        pass_english   = res[3];
        visit_english  = res[4];
        insertion_date = res[5];
        pass_hebrew    = res[6];
        visit_hebrew   = res[7];
        total          = get_words_count(mode, minId, maxId, maxRatio, minVisits, onlyNew, method, maxRecords);

        if mode == 'En2He':
            src = english;
            to = hebrew;
            passed = pass_english;
            visited = visit_english;
        else:
            src = hebrew;
            to = english;
            passed = pass_hebrew;
            visited = visit_hebrew;

        data = {
            "id": id,
            "from": src,
            "to": to,
            "date": insertion_date,
            "pass": passed,
            "visit": visited,
            "total": total
        };
    elif op == "PASS":
        res = update_word(mode=mode, id=id, status="PASS");
        data = {
            "id": id
        }
    elif op == "FAIL":
        res = update_word(mode=mode, id=id, status="FAIL");
        data = {
            "id": id
        }
    elif op == "NEW":
        id = new_word(eng=new_eng, heb=new_heb);
        data = {
            "id": id
        }
    else:
        print("ERROR: no such op", op);

    print("DATA:");
    print(data);
    response = JsonResponse(data);
    response['Access-Control-Allow-Origin'] = '*';
    print("OK\n\n\n");
    return response;

def get_words_count(mode="En2He", minId=0, maxId=5000, maxRatio=0.0, minVisits=3, onlyNew='False', method='random', maxRecords=1):
    db = r"C:\Users\luri\Documents\Personal\dev\django\korakora\korakora\vocabulary.sqlite";
    con = sqlite3.connect(db);
    cur = con.cursor()

    sql = "SELECT count(*) from words_english"
    if onlyNew == 'True':
        sql = sql + " where visit_english=0;"
    else:
        sql = sql + " where id>=" + str(minId) + " and id<=" + str(maxId);
        if mode == "En2He":
            sql = sql + " and (((pass_english*1.0 / visit_english) <= " + str(maxRatio) + ")";
            sql = sql + " or (visit_english < " + str(minVisits) + "));";
        elif mode == "He2En":
            sql = sql + " and (((pass_hebrew*1.0 / visit_hebrew) <= " + str(maxRatio) + ")";
            sql = sql + " or (visit_hebrew < " + str(minVisits) + "));";
        else:
            print("ERROR: no such mode:" + mode);

    print("COUNT SQL:")
    print(sql)
    cur.execute(sql);
    rows = cur.fetchall();
    row = rows[0]
    count = row[0]
    con.close();
    return count



def get_words_from_db(mode="En2He", minId=0, maxId=5000, maxRatio=1, minVisits=1, onlyNew='False', method='random', maxRecords=1):
    db = r"C:\Users\luri\Documents\Personal\dev\django\korakora\korakora\vocabulary.sqlite";
    con = sqlite3.connect(db);
    cur = con.cursor()

    sql = "SELECT id, english, hebrew, pass_english, visit_english, insertion_date, pass_hebrew, visit_hebrew from words_english"
    if onlyNew == 'True':
        sql = sql + " where visit_english=0;"
    else:
        sql = sql + " where id>=" + str(minId) + " and id<=" + str(maxId);
        if mode == "En2He":
            sql = sql + " and (((pass_english*1.0 / visit_english) <= " + str(maxRatio) + ")";
            sql = sql + " or (visit_english < " + str(minVisits) + "));";
        elif mode == "He2En":
            sql = sql + " and (((pass_hebrew*1.0 / visit_hebrew) <= " + str(maxRatio) + ")";
            sql = sql + " or (visit_hebrew < " + str(minVisits) + "));";
        else:
            print("ERROR: no such mode:" + mode);

    print("******* SQL: ");
    print(sql)


    cur.execute(sql);
    rows = cur.fetchall();
    num = len(rows);
    print("Found " + str(num) + " rows");

    if method == 'random':
        rn = randint(0, num-1);
        print("rn=", rn);
        row = rows[rn];
    else:
        for row in rows:
            if row is not None:
                pass
                #print(row[0]);

    con.close();

    print("******* RES: ", row);
    return row;

def update_word(mode='En2He', id=0, status='PASS'):

    print("UPDATE_WORD", mode, id, status)
    db = r"C:\Users\luri\Documents\Personal\dev\django\korakora\korakora\vocabulary.sqlite";
    con = sqlite3.connect(db);
    cur = con.cursor()

    visited = 0;
    passed = 0;

    sql = "SELECT id, english, hebrew, pass_english, visit_english, insertion_date, pass_hebrew, visit_hebrew from words_english where id=" + str(id);
    print(sql);

    cur.execute(sql);
    rows = cur.fetchall();
    row = rows[0]

    if mode == "En2He":
        passed = row[3];
        visited = row[4];
    elif mode == "He2En":
        passed = row[6];
        visited = row[7];
    else:
        print("ERROR");

    print("passed:" + str(passed) + " visited:" + str(visited));

    if status == "PASS":
        passed = passed + 1;

    visited = visited + 1;

    print("passed:" + str(passed) + " visited:" + str(visited));

    if mode == "En2He":
        sql = "UPDATE words_english SET visit_english=" + str(visited) + ", pass_english=" + str(passed) + " where id=" + str(id) + ";"
    elif mode == "He2En":
        sql = "UPDATE words_english SET visit_hebrew=" + str(visited) + ", pass_hebrew=" + str(passed) + " where id=" + str(id) + ";"
    else:
        print("ERROR");

    print(sql);
    cur.execute(sql);
    con.commit();
    con.close();

def new_word(eng=None, heb=None):
    if eng is None:
        return 0
    if heb is None:
        return 0

    db = r"C:\Users\luri\Documents\Personal\dev\django\korakora\korakora\vocabulary.sqlite";
    con = sqlite3.connect(db);
    cur = con.cursor()

    sql = 'SELECT max(id) from words_english'
    cur.execute(sql);
    rows = cur.fetchall();
    row = rows[0]
    id = row[0]

    id = id + 1;
    print("NEW ID:" + str(id));

    sql = "INSERT INTO words_english VALUES (" + str(id) + ",'" + eng + "','" + heb + "', 0, 0, date(), 0, 0);";

    print("SQL:");
    print(sql)

    cur.execute(sql);
    con.commit();
    con.close();

    return 5;

