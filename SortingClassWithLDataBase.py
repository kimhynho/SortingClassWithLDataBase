#학생 성적을 데이터베이스(SQLite)에 저장하고 관리하는 프로그램. 
#기능 요약:
#학생 성적 입력: 학번, 이름, 점수 입력해서 DB에 저장함
#전체 출력: 모든 학생 정보(총점, 평균, 학점, 등수 포함)를 보여줌
#등수 계산: 총점 기준으로 정렬해서 등수 자동 계산하고 DB에 반영
#성적 삭제: 학번으로 찾아서 해당 학생 정보 삭제
#학생 검색: 학번이나 이름으로 학생 한 명 검색
#총점 정렬: 총점 순으로 학생 목록 정렬해서 보여줌
#평균 80 이상인 학생 수 확인: 조건 맞는 학생 수 카운트해서 출력함

import sqlite3

# 학생 클래스
class Student:
    def __init__(self, hakbun, name, eng, c, py, total=None, avg=None, grade=None, rank=0):
        self.hakbun = hakbun
        self.name = name
        self.eng = eng
        self.c = c
        self.py = py
        self.total = total if total is not None else eng + c + py  # 총점 계산
        self.avg = avg if avg is not None else self.total / 3  # 평균도 계산하고
        self.grade = grade if grade else self.get_grade()  # 학점도 계산함
        self.rank = rank  # 등수는 나중에 넣음

    # 학점 계산하는 함수~ 대충 기준 나눠서 줌
    def get_grade(self):
        if self.avg >= 90:
            return 'A'
        elif self.avg >= 80:
            return 'B'
        elif self.avg >= 70:
            return 'C'
        elif self.avg >= 60:
            return 'D'
        else:
            return 'F'

    # 출력할 때 이쁘게 나오게 해주는거
    def __str__(self):
        return f"{self.hakbun}\t{self.name}\t{self.eng}\t{self.c}\t{self.py}\t{self.total}\t{self.avg:.1f}\t{self.grade}\t{self.rank}"


# 이제 전체 학생들 관리하는 클래스
class StudentManager:
    def __init__(self):
        self.conn = sqlite3.connect("student.db")  # DB 연결함
        self.create_table()  # 테이블 없으면 만들고

    # 테이블 있으면 안만듬
    def create_table(self):
        c = self.conn.cursor()
        c.execute('''
            CREATE TABLE IF NOT EXISTS students (
                hakbun TEXT PRIMARY KEY,
                name TEXT,
                eng INTEGER,
                c INTEGER,
                py INTEGER,
                total INTEGER,
                avg REAL,
                grade TEXT,
                rank INTEGER
            )
        ''')
        self.conn.commit()

    # 입력하는 함수임. 유저한테 값 받음
    def input_score(self):
        print("== 학생 정보 입력 ==")
        hakbun = input("학번: ")
        name = input("이름: ")
        eng = int(input("영어 점수: "))
        c_score = int(input("C언어 점수: "))
        py = int(input("파이썬 점수: "))
        s = Student(hakbun, name, eng, c_score, py)

        with self.conn:
            self.conn.execute('''
                INSERT OR REPLACE INTO students VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (s.hakbun, s.name, s.eng, s.c, s.py, s.total, s.avg, s.grade, s.rank))
        print("입력 완료 \n")

    # 전체 다 보여주는 거임
    def print_all(self):
        print("학번\t이름\t영어\tC\t파이썬\t총점\t평균\t학점\t등수")
        c = self.conn.cursor()
        for row in c.execute("SELECT * FROM students ORDER BY rank ASC"):
            s = Student(*row)
            print(s)

    # 등수 계산하는 함수인데 걍 총점 높은 순으로 정렬해서 1등부터 주는 거임
    def calc_rank(self):
        c = self.conn.cursor()
        students = list(c.execute("SELECT * FROM students"))
        students.sort(key=lambda x: x[5], reverse=True)  # 5번 인덱스가 total임

        for idx, student in enumerate(students):
            rank = idx + 1  # 1등부터 시작
            self.conn.execute("UPDATE students SET rank = ? WHERE hakbun = ?", (rank, student[0]))
        self.conn.commit()

        # 끝나고 출력까지 해줌 (봐야 하니까)
        print("등수 계산됨, 결과 출력:")
        print("학번\t이름\t영어\tC\t파이썬\t총점\t평균\t학점\t등수")
        for student in students:
            s = Student(*student)
            print(s)

    # 삭제하는 함수. 학번으로 삭제함
    def delete_student(self):
        hakbun = input("삭제할 학생 학번 입력: ")
        c = self.conn.cursor()
        c.execute("DELETE FROM students WHERE hakbun = ?", (hakbun,))
        self.conn.commit()
        if c.rowcount:
            print("삭제 완료!")  # 있으면 삭제됨
        else:
            print("그런 학번 없음")  # 없으면 못 지움

    # 찾기 기능인데 학번이나 이름 아무거나 써도 찾음
    def search_student(self):
        key = input("학번이나 이름으로 검색: ")
        c = self.conn.cursor()
        c.execute("SELECT * FROM students WHERE hakbun = ? OR name = ?", (key, key))
        row = c.fetchone()
        if row:
            print("찾음")
            print("학번\t이름\t영어\tC\t파이썬\t총점\t평균\t학점\t등수")
            print(Student(*row))
        else:
            print("못찾음")  # 없으면 걍 못찾음

    # 총점순 정렬하는 거. 등수도 같이 계산해서 출력함
    def sort_total(self):
        print("총점 기준 정렬 출력")
        self.calc_rank()  # 이게 내부적으로 출력까지 함
        # 따로 출력 안 해도 됨

    # 평균 80 넘는 애들 몇 명인지 보는 거임
    def count_over_80(self):
        c = self.conn.cursor()
        c.execute("SELECT COUNT(*) FROM students WHERE avg >= 80")
        count = c.fetchone()[0]
        print("평균 80점 넘는 사람:", count, "명")


# 이제 메인임. 걍 메뉴 돌리는 while문
def main():
    manager = StudentManager()
    while True:
        print("\n====== 학생 성적 관리 (DB버전) ======")
        print("1. 성적 입력")
        print("2. 전체 출력")
        print("3. 등수 계산")
        print("4. 성적 삭제")
        print("5. 학생 검색")
        print("6. 총점 정렬")
        print("7. 평균 80점 넘는 사람 몇명인지 보기")
        print("8. 종료")

        choice = input("번호 고르셈: ")
        if choice == '1':
            manager.input_score()
        elif choice == '2':
            manager.print_all()
        elif choice == '3':
            manager.calc_rank()
        elif choice == '4':
            manager.delete_student()
        elif choice == '5':
            manager.search_student()
        elif choice == '6':
            manager.sort_total()
        elif choice == '7':
            manager.count_over_80()
        elif choice == '8':
            print("종료")  # 걍 종료함
            break
        else:
            print("잘못 누름;;")  # 1~8 아니면 걍 틀림


# 이건 파이썬 돌릴 때 실행되게 하는 거
if __name__ == "__main__":
    main()
