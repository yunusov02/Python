#include <assert.h>
#include <stdbool.h>
#include <stdio.h>
#include <string.h>

#define MAX_NAME 256
#define TABLE_SIZE 10

typedef struct {
    char name[MAX_NAME];
    int age;
} person;

person *hash_table[TABLE_SIZE];

unsigned int hash(const char *name) {
    unsigned int hashed_value = 0;

    for (int i = 0; name[i] != '\0'; i++) {
        hashed_value += (unsigned char) name[i];
        hashed_value = (hashed_value * (unsigned char) name[i]) % TABLE_SIZE;
    }

    return hashed_value;
}

void init_hash_table(void) {
    for (int i = 0; i < TABLE_SIZE; i++) {
        hash_table[i] = NULL;
    }
}

void print_table(void) {
    printf("Start\n");

    for (int i = 0; i < TABLE_SIZE; i++) {
        if (hash_table[i] == NULL) {
            printf("\t%i\t---\n", i);
        } else {
            printf("\t%i\t%s (%d)\n", i, hash_table[i]->name, hash_table[i]->age);
        }
    }

    printf("End\n");
}

bool hash_table_insert(person *p) {
    if (p == NULL) {
        return false;
    }

    unsigned int index = hash(p->name);

    for (int i = 0; i < TABLE_SIZE; i++) {
        unsigned int try = (index + i) % TABLE_SIZE;

        if (hash_table[try] == NULL) {
            hash_table[try] = p;
            return true;
        }
    }

    return false;
}

person *hash_table_lookup(const char *name) {
    unsigned int index = hash(name);

    for (int i = 0; i < TABLE_SIZE; i++) {
        unsigned int try = (index + i) % TABLE_SIZE;

        if (hash_table[try] != NULL && strcmp(hash_table[try]->name, name) == 0) {
            return hash_table[try];
        }
    }

    return NULL;
}

person *hash_table_delete(const char *name) {
    unsigned int index = hash(name);

    for (int i = 0; i < TABLE_SIZE; i++) {
        unsigned int try = (index + i) % TABLE_SIZE;

        if (hash_table[try] != NULL && strcmp(hash_table[try]->name, name) == 0) {
            person *tmp = hash_table[try];
            hash_table[try] = NULL;
            return tmp;
        }
    }

    return NULL;
}

int main(void) {
    person jacob = {.name = "Jacob", .age = 256};
    person tom = {.name = "Tom", .age = 56};
    person alex = {.name = "alex", .age = 156};
    person john = {.name = "john", .age = 26};

    init_hash_table();



    hash_table_insert(&jacob);
    hash_table_insert(&tom);
    hash_table_insert(&alex);
    hash_table_insert(&john);

    print_table();

    assert(hash_table_lookup("George") == NULL);
    assert(hash_table_lookup("alex") == &alex);
    assert(hash_table_lookup("alex")->age == 156);

    person *tmp = hash_table_delete("alex");

    print_table();

    return 0;
}
