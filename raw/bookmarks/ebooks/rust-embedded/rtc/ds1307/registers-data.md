# [Details of Time Data Bits](#details-of-time-data-bits){.header}

Now let\'s look at how the data is stored inside each register. Remember, each register holds 8 bits (bit 7 to bit 0), and the time values are stored in BCD format.

`<style>
  .styled-table {
    width: 100%;
    border-collapse: collapse;
    font-family: "Roboto", Arial, sans-serif;
    font-size: 14px;
    text-align: center;
    border-radius: 6px;
    overflow: hidden;
    box-shadow: 0 2px 6px rgba(0,0,0,0.15);
  }

  .styled-table th {
    background-color: #1c1c1c;
    color: #ffffff;
    padding: 10px;
    font-weight: 600;
    border: 1px solid #424242;
  }

  .styled-table td {
    padding: 10px;
    border: 1px solid #424242;
  }

  .styled-tr:nth-child(even) {
    background-color: #2e2e2e;
  }

  .register-name {
    background-color: #3a3a3a;
    color: #ffffff;
    font-weight: 600;
    text-align: left;
    padding-left: 12px;
  }

  .special-bit {
    background-color: #bf360c;
    color: #ffffff;
    font-weight: 500;
  }

  .fixed-bit {
    background-color: #546e7a;
    color: #ffffff;
  }

  .group-tens {
    background-color: #1565c0;
    color: #ffffff;
    font-weight: 500;
  }

  .group-ones {
    background-color: #2e7d32;
    color: #ffffff;
    font-weight: 500;
  }
</style>`{=html}

+----------+----------+--------------+--------------------------------+---------------------+----------+----------+----------+----------+
| REGISTER | BIT 7    | BIT 6        | BIT 5                          | BIT 4               | BIT 3    | BIT 2    | BIT 1    | BIT 0    |
+==========+==========+==============+================================+=====================+==========+==========+==========+==========+
| Seconds  | CH       | Tens digit of seconds                                               | Ones digit of seconds                     |
+----------+----------+---------------------------------------------------------------------+-------------------------------------------+
| Minutes  | 0        | Tens digit of minutes                                               | Ones digit of minutes                     |
+----------+----------+--------------+--------------------------------+---------------------+-------------------------------------------+
| Hours    | 0        | Select\      | PM/AM Flag in 12 hour format\  | Tens digit of hours | Ones digit of hours                       |
|          |          | 12/24 format | or\                            |                     |                                           |
|          |          |              | Part of Tens in 24 hour format |                     |                                           |
+----------+----------+--------------+--------------------------------+---------------------+----------+--------------------------------+
| Day      | 0        | 0            | 0                              | 0                   | 0        | Day value (1-7)                |
+----------+----------+--------------+--------------------------------+---------------------+----------+--------------------------------+
| Date     | 0        | 0            | Tens digit of date                                   | Ones digit of date                        |
+----------+----------+--------------+--------------------------------+---------------------+-------------------------------------------+
| Month    | 0        | 0            | 0                              | Tens digit of month | Ones digit of month                       |
+----------+----------+--------------+--------------------------------+---------------------+-------------------------------------------+
| Year     | Tens digit of year                                                             | Ones digit of year                        |
+----------+--------------------------------------------------------------------------------+-------------------------------------------+

## [Seconds: Range 00-59](#seconds-range-00-59){.header}

The bits 0-3 represent the ones digit part of the seconds. The bits 4-6 represent the tens digit part of the seconds.

If you want to represent seconds 30, the BCD format will be: 0011 0000. So, we will put 011 in bits 4-6 (tens digit) and 0000 in bits 0-3 (ones digit).

``` sh
Bit:     7 6 5 4 3 2 1 0
Value:   0 0 1 1 0 0 0 0
         │ └─┬─┘ └──┬──┘
         │   3      0
         CH bit
```

CH bit (bit 7) controls clock halt - it\'s like an on/off switch for the entire clock (1 = clock stopped, 0 = clock running).

## [Minutes: Range 00-59](#minutes-range-00-59){.header}

The bits 0-3 represent the ones digit part of the minutes. The bits 4-6 represent the tens digit part of the minutes.

If you want to represent minutes 45, the BCD format will be: 0100 0101. So, we will put 100 in bits 4-6 (tens digit) and 0101 in bits 0-3 (ones digit).

``` sh
Bit:     7 6 5 4 3 2 1 0
Value:   0 1 0 0 0 1 0 1
         │ └─┬─┘ └──┬──┘
         │   4      5
         Always 0
```

Bit 7 is always 0.

## [Hours: Range 1-12 + AM/PM (12-hour mode) or 00-23 (24-hour mode)](#hours-range-1-12--ampm-12-hour-mode-or-00-23-24-hour-mode){.header} {#hours-range-1-12--ampm-12-hour-mode-or-00-23-24-hour-mode}

In 12-hour mode:

- Bit 6 = 1 (selects 12-hour format)
- Bit 5 = AM/PM bit (0=AM, 1=PM)
- Bit 4 = tens digit of hour (0 or 1)
- Bits 3-0 = ones digit of hour

In 24-hour mode:

- Bit 6 = 0 (selects 24-hour format)
- Bits 5-4 = tens digit of hour
- Bits 3-0 = ones digit of hour

> Important: The hours value must be re-entered whenever the 12/24-hour mode bit is changed.

If you want to represent 2 PM in 12-hour mode, the format will be: 0110 0010. So bit 6=1 (12-hour), bit 5=1 (PM), bit 4=0 (tens digit), bits 3-0 will be 0010 (ones digit).

``` sh
Bit:     7 6 5 4 3 2 1 0
Value:   0 1 1 0 0 0 1 0
         │ │ │ │ └──┬──┘
         │ │ │ │    2
         │ │ │ tens digit
         │ │ PM bit
         │ 12-hour format
         Always 0
```

If you want to represent 14:00 in 24-hour mode, the format will be: 0001 0100. So bit 6=0 (24-hour), bits 5-4 will be 01 (tens digit), bits 3-0 will be 0100 (ones digit).

``` sh
Bit:     7 6 5 4 3 2 1 0
Value:   0 0 0 1 0 1 0 0
         │ │ └┬┘ └──┬──┘
         │ │  1     4
         │ 24-hour format
         Always 0
```

## [Day: Range 01-07 (1=Sunday, 2=Monday, etc.)](#day-range-01-07-1sunday-2monday-etc){.header} {#day-range-01-07-1sunday-2monday-etc}

The bits 0-2 represent the day value. Bits 3-7 are always 0.

If you want to represent Tuesday (day 3), the format will be: 0000 0011.

``` sh
Bit:     7 6 5 4 3 2 1 0
Value:   0 0 0 0 0 0 1 1
         └───┬───┘ └─┬─┘
         Always 0     3
```

## [Date: Range 01-31 (day of month)](#date-range-01-31-day-of-month){.header}

The bits 0-3 represent the ones digit part of the date. The bits 4-5 represent the tens digit part of the date.

If you want to represent date 25, the BCD format will be: 0010 0101. So, we will put 10 in bits 4-5 (tens digit) and 0101 in bits 0-3 (ones digit).

``` sh
Bit:     7 6 5 4 3 2 1 0
Value:   0 0 1 0 0 1 0 1
         └┬┘ └┬┘ └──┬──┘
          0   2     5
         Always 0
```

Bits 6-7 are always 0.

## [Month: Range 01-12](#month-range-01-12){.header}

The bits 0-3 represent the ones digit part of the month. Bit 4 represents the tens digit part of the month.

If you want to represent month 12 (December), the BCD format will be: 0001 0010. So, we will put 1 in bit 4 (tens digit) and 0010 in bits 0-3 (ones digit).

``` sh
Bit:     7 6 5 4 3 2 1 0
Value:   0 0 0 1 0 0 1 0
         └─┬─┘ │ └──┬──┘
     Always 0  1    2
```

Bits 5-7 are always 0.

## [Year: Range 00-99 (represents 2000-2099)](#year-range-00-99-represents-2000-2099){.header}

The bits 0-3 represent the ones digit part of the year. The bits 4-7 represent the tens digit part of the year.

If you want to represent year 23 (2023), the BCD format will be: 0010 0011. So, we will put 0010 in bits 4-7 (tens digit) and 0011 in bits 0-3 (ones digit).

``` sh
Bit:     7 6 5 4 3 2 1 0
Value:   0 0 1 0 0 0 1 1
         └──┬──┘ └──┬──┘
            2      3
```

Remember when I first mentioned the DS1307 and how it could only represent dates until 2100? I was curious about that limitation too. Well, Now we\'ve identified the culprit: the DS1307\'s 8-bit year register can only store two digits (00-99) in BCD format, and the chip assumes these always represent years in the 2000s century.
