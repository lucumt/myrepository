package com.lucumt;

public class SmallIntBitCompressTest {

    public static void main(String[] args) {
        testData();
    }

    public static void testData() {
        int x = -14997;
        int y = -3349;
        int z = -2377;
        long target = 0;
        target = bitWrite(1, x, target);
        target = bitWrite(2, y, target);
        target = bitWrite(3, z, target);
        System.out.println(target);
        target = 576508581063426599L;
        System.out.println(Long.toBinaryString(target));
        System.out.println(bitRead(1, target));
        System.out.println(bitRead(2, target));
        System.out.println(bitRead(3, target));
    }

    public static long bitWrite(int position, long original, long target) {
        long typeBase = 1L << (position * 20 - 1);
        long valueBase = 0x7ffffL << ((position - 1) * 20);
        if (original < 0) {
            target = target | typeBase;
            original = -original;
        }
        original = original << (position - 1) * 20;
        original = original & valueBase;
        target = target | original;
        return target;
    }

    public static long bitRead(int position, long target) {
        long value;
        long typeBase = 1L << (position * 20 - 1);
        boolean isNegative = (target & typeBase) == typeBase;

        long valueBase = 0x7ffffL << ((position - 1) * 20);
        value = target & valueBase;
        value = value >> (position - 1) * 20;

        if (isNegative) {
            value = -value;
        }
        return value;
    }
}
