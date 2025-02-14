import curses
import my_netsnmp

def draw_table(stdscr):
    curses.init_pair(1, curses.COLOR_BLACK, curses.COLOR_WHITE)
    curses.init_pair(3, curses.COLOR_BLACK, curses.COLOR_WHITE)
    if curses.can_change_color():
        curses.init_pair(1, 63, 252)
        curses.init_pair(2, 0, 252)
        stdscr.bkgd(' ', curses.color_pair(2))
    stdscr.clear()
    stdscr.nodelay(True)

    status_str = "MPOD HV readout via snmp. Press q to exit"
    stdscr.addstr(0,0, status_str, curses.color_pair(1))
    do_exit = False
    loop_cnt = 10
    while not do_exit:
        if loop_cnt == 10:
            stdscr.addstr(2, 0, my_netsnmp.show_info())
            stdscr.addstr(11,0, "..........", curses.color_pair(3))
            stdscr.refresh()
            loop_cnt = 0

        stdscr.addstr(8,0, my_netsnmp.show_amp_meas())
        stdscr.addstr(11,loop_cnt, "-", curses.color_pair(3))
        stdscr.move(13,0)
        stdscr.refresh()

        user_input = ""
        try:
            user_input = stdscr.getkey()
        except curses.error:
            pass
        if user_input == "q": do_exit = True

        loop_cnt += 1
        curses.napms(1000)

if __name__ == "__main__":
    curses.wrapper(draw_table)