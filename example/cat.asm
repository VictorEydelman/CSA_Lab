_start:
      ei
      load_symbol
      push 10
      sub
      jz print
      jmp _start
  print:
      load
      store
      halt