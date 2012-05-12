#
# Copyright 2012 Ralf Kistner
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.



"""
Some functionality concerning prime numbers and number theory.
"""

def calculate_primes(limit):
    """
    Calculates all primes <= limit.
    
    >>> calculate_primes(10)
    [2, 3, 5, 7]
    >>> calculate_primes(3)
    [2, 3]
    """
    limit += 1
    is_prime = [True]*limit
    is_prime[0] = False
    is_prime[1] = False
    primes = []
    for i in range(2, limit):
        if not is_prime[i]:
            continue
        primes.append(i)
        for j in range(2*i, limit, i):
            is_prime[j] = False
    return primes
    
def factorise(number, primes=None):
    """
    Given a sorted list of primes, factorises a number.
    
    >>> factorise(5)
    [(5, 1)]
    >>> factorise(12)
    [(2, 2), (3, 1)]
    >>> factorise(12, [2, 3])
    [(2, 2), (3, 1)]
    >>> factorise(39, [2, 3, 5, 7])
    [(3, 1), (13, 1)]
    
    Note the result of the following example, where 5 is not in the provided list of primes.
    >>> factorise(75, [2, 3])
    [(3, 1), (25, 1)]
    """
    if primes is None:
        import math
        primes = calculate_primes(int(math.sqrt(number)))
    
    factors = []
    for p in primes:
        if p > number:
            break
        count = 0
        while number % p == 0:
            number //= p
            count += 1
        if count > 0:
            factors.append((p, count))
    # This last check allows us to factorise numbers up to p^2 with only pre-calculated primes up to p
    if number > 1:
        factors.append((number, 1))
    return factors