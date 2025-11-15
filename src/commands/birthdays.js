const { SlashCommandBuilder, EmbedBuilder } = require('discord.js');
const { getBirthdays } = require('../database');

module.exports = {
    data: new SlashCommandBuilder()
        .setName('birthdays')
        .setDescription('Kayıtlı doğum günlerini gösterir.'),
    async execute(interaction) {
        await interaction.deferReply();

        getBirthdays(interaction.guild.id, (birthdays) => {
            if (birthdays.length === 0) {
                return interaction.followUp('❌ Henüz kayıtlı doğum günü yok.');
            }

            const birthdayList = birthdays
                .map(b => `<@${b.user_id}>: ${b.day}/${b.month}`)
                .join('\n');

            const embed = new EmbedBuilder()
                .setColor('#0099ff')
                .setTitle('🎂 Kayıtlı Doğum Günleri')
                .setDescription(birthdayList)
                .setTimestamp();

            interaction.followUp({ embeds: [embed] });
        });
    }
};
